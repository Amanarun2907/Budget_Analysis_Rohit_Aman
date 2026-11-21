import os
import re
import json
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()


class DocumentProcessor:
    """
    Processes uploaded budget documents.

    Outputs a dict with keys:
      - text       : full extracted text with page markers
      - tables     : list of table dicts {data, source_page}
      - metadata   : detected properties (year, gov level, state, doc type)
      - page_count : integer
    """

    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
        "Andaman and Nicobar", "Dadra and Nagar Haveli", "Daman and Diu", "Lakshadweep",
    ]

    # ─────────────────────── dispatch ───────────────────────────────────────

    async def process_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        try:
            logger.info("Processing document", path=file_path, type=file_type)
            ext = file_type.lower().lstrip(".")

            dispatch = {
                "pdf":  self._process_pdf,
                "docx": self._process_docx,
                "xlsx": self._process_excel,
                "xls":  self._process_excel,
                "csv":  self._process_csv,
                "txt":  self._process_text,
                "text": self._process_text,
                "jpg":  self._process_image,
                "jpeg": self._process_image,
                "png":  self._process_image,
            }
            handler = dispatch.get(ext, self._process_fallback)
            return await handler(file_path)

        except Exception as e:
            logger.error("Document processing error", error=str(e), path=file_path)
            return {"text": "", "tables": [], "metadata": {"error": str(e)}, "page_count": 0}

    # ─────────────────────── PDF ─────────────────────────────────────────────

    async def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Fast, latency-optimized PDF extraction with intelligent page prioritization.
        - Text extracted across all pages in under 1 second.
        - Table extraction prioritizes high-value summary pages containing key financial terms.
        - Hard cap of 20 tables max prevents CPU exhaustion and multi-minute freezing.
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            full_text = ""
            tables: List[Dict] = []
            page_count = len(doc)

            # High-priority keywords that indicate financial summary tables
            TABLE_KEYWORDS = (
                "receipt", "expenditure", "deficit", "statement", "crore",
                "rupees", "glance", "summary", "fiscal", "capital", "revenue",
                "allocation", "be ", "re ", "actual"
            )

            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text("text") or ""
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"

                # Only search for vector tables on pages likely to contain summary tables,
                # or the first 20 pages, and stop once we have 20 high-quality tables.
                tl = text.lower()
                is_high_value_page = page_num < 20 or any(k in tl for k in TABLE_KEYWORDS)

                if is_high_value_page and len(tables) < 20:
                    try:
                        page_tables = page.find_tables()
                        for tbl in page_tables:
                            if len(tables) >= 20:
                                break
                            data = tbl.extract()
                            if data and len(data) >= 2:
                                tables.append({
                                    "table_index": len(tables),
                                    "data": [[str(c or "").strip() for c in row] for row in data],
                                    "source_page": page_num + 1,
                                })
                    except Exception:
                        if len(tables) < 20:
                            page_tables = self._extract_tables_heuristic(text, page_num + 1)
                            tables.extend(page_tables[:20 - len(tables)])

            metadata = {
                "page_count": page_count,
                "title":  (doc.metadata or {}).get("title", "") or "",
                "author": (doc.metadata or {}).get("author", "") or "",
            }
            doc.close()

            detected = self._detect_properties(full_text)
            metadata.update(detected)

            return {
                "text":       full_text,
                "tables":     tables,
                "metadata":   metadata,
                "page_count": metadata["page_count"],
            }

        except ImportError:
            logger.warning("PyMuPDF not installed — reading PDF as raw bytes")
            with open(file_path, "rb") as f:
                raw = f.read()
            text = raw.decode("utf-8", errors="ignore")
            detected = self._detect_properties(text)
            return {
                "text":       text,
                "tables":     self._extract_tables_heuristic(text, 1),
                "metadata":   detected,
                "page_count": 1,
            }

    # ─────────────────────── Image OCR ──────────────────────────────────────

    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="eng")
            detected = self._detect_properties(text)
            return {
                "text":       text,
                "tables":     self._extract_tables_heuristic(text, 1),
                "metadata":   {"page_count": 1, "ocr": True, **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return {
                "text":       f"[Image file: {os.path.basename(file_path)}]",
                "tables":     [],
                "metadata":   {"page_count": 1, "ocr_error": str(e)},
                "page_count": 1,
            }

    # ─────────────────────── DOCX ───────────────────────────────────────────

    async def _process_docx(self, file_path: str) -> Dict[str, Any]:
        try:
            from docx import Document

            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs)

            tables: List[Dict] = []
            for i, table in enumerate(doc.tables):
                data = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                if data:
                    tables.append({"table_index": i, "data": data, "source_page": 1})

            detected = self._detect_properties(full_text)
            return {
                "text":       full_text,
                "tables":     tables,
                "metadata":   {"page_count": 1, **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"DOCX fallback: {e}")
            return await self._process_text(file_path)

    # ─────────────────────── Excel ──────────────────────────────────────────

    async def _process_excel(self, file_path: str) -> Dict[str, Any]:
        try:
            import pandas as pd

            xl = pd.ExcelFile(file_path)
            full_text = ""
            tables: List[Dict] = []

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
                df = df.fillna("")
                full_text += f"\n--- Sheet: {sheet_name} ---\n{df.to_string()}\n"
                data = [df.columns.tolist()] + df.values.tolist()
                tables.append({
                    "table_index": len(tables),
                    "sheet":       sheet_name,
                    "data":        [[str(c) for c in row] for row in data],
                    "source_page": 1,
                })

            detected = self._detect_properties(full_text)
            return {
                "text":       full_text,
                "tables":     tables,
                "metadata":   {"page_count": len(xl.sheet_names), **detected},
                "page_count": len(xl.sheet_names),
            }
        except Exception as e:
            logger.warning(f"Excel read error: {e}")
            return await self._process_fallback(file_path)

    # ─────────────────────── CSV ─────────────────────────────────────────────

    async def _process_csv(self, file_path: str) -> Dict[str, Any]:
        try:
            import pandas as pd

            df = pd.read_csv(file_path, dtype=str).fillna("")
            full_text = df.to_string()
            data = [df.columns.tolist()] + df.values.tolist()
            detected = self._detect_properties(full_text)
            return {
                "text":       full_text,
                "tables":     [{"table_index": 0, "data": [[str(c) for c in row] for row in data], "source_page": 1}],
                "metadata":   {"page_count": 1, "rows": len(df), **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"CSV error: {e}")
            return await self._process_text(file_path)

    # ─────────────────────── Plain text ─────────────────────────────────────

    async def _process_text(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        detected = self._detect_properties(text)
        return {
            "text":       text,
            "tables":     self._extract_tables_heuristic(text, 1),
            "metadata":   {"page_count": 1, **detected},
            "page_count": 1,
        }

    # ─────────────────────── Fallback ────────────────────────────────────────

    async def _process_fallback(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = f"[Binary file: {os.path.basename(file_path)}]"
        detected = self._detect_properties(text)
        return {"text": text, "tables": [], "metadata": detected, "page_count": 1}

    # ─────────────────────── heuristic table extraction ─────────────────────

    def _extract_tables_heuristic(self, text: str, page_num: int) -> List[Dict]:
        """
        Extract table-like structures from plain text.
        A 'table row' has ≥2 numbers separated by whitespace or pipes.
        """
        tables: List[Dict] = []
        rows: List[List[str]] = []

        for line in text.split("\n"):
            nums = re.findall(r"[\d,]+\.?\d*", line)
            if len(nums) >= 2 and len(line.strip()) > 8:
                # Split on 2+ spaces, tabs, or pipes
                parts = [p.strip() for p in re.split(r"\s{2,}|\t|\|", line.strip()) if p.strip()]
                if len(parts) >= 2:
                    rows.append(parts)
                    continue
            # Row break
            if len(rows) >= 2:
                tables.append({
                    "table_index": len(tables),
                    "data":        rows,
                    "source_page": page_num,
                })
            rows = []

        if len(rows) >= 2:
            tables.append({
                "table_index": len(tables),
                "data":        rows,
                "source_page": page_num,
            })

        return tables

    # ─────────────────────── metadata detection ──────────────────────────────

    def _detect_properties(self, text: str) -> Dict[str, Any]:
        """
        Detect: financial year, government level (union/state), state name, document type.
        Uses multiple pattern strategies to maximise accuracy across diverse budget formats.
        """
        props: Dict[str, Any] = {}
        tl = text.lower()

        # ── Financial year ──
        # Try canonical "YYYY-YY" or "YYYY-YYYY" format first
        fy_match = re.search(
            r"\b(20\d{2})[–\-](20\d{2}|\d{2})\b",
            text,
        )
        if fy_match:
            y1   = fy_match.group(1)
            y2   = fy_match.group(2)
            y2_2 = y2[-2:] if len(y2) == 4 else y2
            props["financial_year"] = f"{y1}-{y2_2}"
        else:
            # Fallback patterns
            for pat in [
                r"financial\s+year\s+(20\d{2})",
                r"budget\s+(20\d{2})",
                r"fy\s*(20\d{2})",
            ]:
                m = re.search(pat, tl)
                if m:
                    y = m.group(1)
                    props["financial_year"] = f"{y}-{int(y[2:])+1:02d}"
                    break

        if "financial_year" not in props:
            # Cannot determine year from document — leave null rather than fabricating a year.
            # The UI will show "Not specified" and the LLM agents will also attempt extraction.
            props["financial_year"] = None

        # ── State or Union detection ──
        # Check explicit State signals first: "government of <state>", "<state> state budget", "finance department"
        detected_state: Optional[str] = None
        for state in self.INDIAN_STATES:
            s_lower = state.lower()
            # Explicit patterns indicating state budget document
            if (
                f"government of {s_lower}" in tl
                or f"{s_lower} state budget" in tl
                or f"{s_lower} budget" in tl
                or f"state of {s_lower}" in tl
            ):
                detected_state = state
                break

        # If not found via direct phrases, check state frequency
        if not detected_state:
            for state in self.INDIAN_STATES:
                if tl.count(state.lower()) >= 2:
                    # Make sure it's not a union document mentioning state programs
                    if "union budget" not in tl and "government of india" not in tl:
                        detected_state = state
                        break

        union_signals = [
            "union budget", "government of india", "consolidated fund of india",
            "parliament of india", "lok sabha", "rajya sabha",
        ]
        is_union_doc = any(sig in tl for sig in union_signals)

        if detected_state and not ("union budget" in tl and "government of india" in tl and f"government of {detected_state.lower()}" not in tl):
            props["government_level"] = "state"
            props["state_name"]       = detected_state
            props["government_name"]  = f"Government of {detected_state}"
        elif is_union_doc or "union" in tl:
            props["government_level"] = "union"
            props["government_name"]  = "Government of India"
        else:
            props["government_level"] = "union"
            props["government_name"]  = "Government of India"

        # ── Document type ──
        doc_type_map = {
            "budget_speech":              ["budget speech", "speech of", "hon'ble", "finance minister"],
            "annual_financial_statement": ["annual financial statement", "statement i", "consolidated fund"],
            "expenditure_budget":         ["expenditure budget", "expenditure profile", "demand for grants"],
            "receipt_budget":             ["receipt budget", "receipts budget", "revenue receipts"],
            "economic_survey":            ["economic survey", "macroeconomic overview"],
            "fiscal_policy":              ["fiscal policy", "frbm", "medium term fiscal"],
            "budget_highlights":          ["budget highlights", "budget at a glance", "key highlights"],
        }
        for dtype, kws in doc_type_map.items():
            if any(kw in tl for kw in kws):
                props["document_type"] = dtype
                break
        if "document_type" not in props:
            props["document_type"] = "budget_document"

        return props
