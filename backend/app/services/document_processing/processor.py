import os
import re
import json
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()

class DocumentProcessor:
    """Processes uploaded budget documents - extracts text, tables, and metadata."""
    
    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
        "Andaman and Nicobar", "Dadra and Nagar Haveli", "Daman and Diu", "Lakshadweep"
    ]
    
    async def process_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Process a single document and extract all information."""
        try:
            logger.info("Processing document", path=file_path, type=file_type)
            clean_type = file_type.lower().lstrip('.')
            
            if clean_type == "pdf":
                return await self._process_pdf(file_path)
            elif clean_type in ("jpg", "jpeg", "png"):
                return await self._process_image(file_path)
            elif clean_type == "docx":
                return await self._process_docx(file_path)
            elif clean_type in ("xlsx", "xls"):
                return await self._process_excel(file_path)
            elif clean_type == "csv":
                return await self._process_csv(file_path)
            elif clean_type in ("txt", "text"):
                return await self._process_text(file_path)
            else:
                return await self._process_fallback(file_path)
        except Exception as e:
            logger.error("Document processing error", error=str(e), path=file_path)
            return {"text": "", "tables": [], "metadata": {"error": str(e)}, "page_count": 0}
    
    async def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text, tables, and metadata from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            full_text = ""
            tables = []
            page_texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text") or ""
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                page_texts.append({"page": page_num + 1, "text": text})
                
                # Extract tables using text heuristics
                page_tables = self._extract_tables_from_text(text, page_num + 1)
                tables.extend(page_tables)
            
            metadata = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", "") if doc.metadata else "",
                "author": doc.metadata.get("author", "") if doc.metadata else "",
            }
            doc.close()
            
            # Detect document properties
            detected = self._detect_document_properties(full_text)
            metadata.update(detected)
            
            return {
                "text": full_text,
                "tables": tables,
                "metadata": metadata,
                "page_count": len(page_texts),
            }
        except ImportError:
            # Fallback if fitz is not installed yet
            with open(file_path, 'rb') as f:
                raw_bytes = f.read()
            text = raw_bytes.decode('utf-8', errors='ignore')
            detected = self._detect_document_properties(text)
            return {
                "text": text,
                "tables": self._extract_tables_from_text(text, 1),
                "metadata": detected,
                "page_count": 1,
            }
    
    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image file with OCR or fallback."""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='eng')
            detected = self._detect_document_properties(text)
            
            return {
                "text": text,
                "tables": self._extract_tables_from_text(text, 1),
                "metadata": {"page_count": 1, "ocr": True, **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"OCR not available or failed: {e}")
            return {
                "text": f"[Image file uploaded: {os.path.basename(file_path)}]",
                "tables": [],
                "metadata": {"page_count": 1, "ocr_error": str(e)},
                "page_count": 1,
            }
    
    async def _process_docx(self, file_path: str) -> Dict[str, Any]:
        """Process DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs)
            
            tables = []
            for i, table in enumerate(doc.tables):
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                if table_data:
                    tables.append({"table_index": i, "data": table_data, "source_page": 1})
            
            detected = self._detect_document_properties(full_text)
            return {
                "text": full_text,
                "tables": tables,
                "metadata": {"page_count": 1, **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"DOCX extraction fallback: {e}")
            return await self._process_text(file_path)
    
    async def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Process Excel file."""
        try:
            import pandas as pd
            xl = pd.ExcelFile(file_path)
            full_text = ""
            tables = []
            
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                full_text += f"\n--- Sheet: {sheet_name} ---\n"
                full_text += df.to_string()
                
                table_data = [df.columns.tolist()] + df.values.tolist()
                tables.append({
                    "table_index": len(tables),
                    "sheet": sheet_name,
                    "data": [[str(cell) for cell in row] for row in table_data],
                    "source_page": 1,
                })
            
            detected = self._detect_document_properties(full_text)
            return {
                "text": full_text,
                "tables": tables,
                "metadata": {"page_count": len(xl.sheet_names), "sheets": xl.sheet_names, **detected},
                "page_count": len(xl.sheet_names),
            }
        except Exception as e:
            logger.warning(f"Excel read error: {e}")
            return await self._process_fallback(file_path)
    
    async def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process CSV file."""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            full_text = df.to_string()
            table_data = [df.columns.tolist()] + df.values.tolist()
            detected = self._detect_document_properties(full_text)
            
            return {
                "text": full_text,
                "tables": [{"table_index": 0, "data": [[str(c) for c in row] for row in table_data], "source_page": 1}],
                "metadata": {"page_count": 1, "rows": len(df), "columns": len(df.columns), **detected},
                "page_count": 1,
            }
        except Exception as e:
            logger.warning(f"CSV read error: {e}")
            return await self._process_text(file_path)
    
    async def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Process plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        detected = self._detect_document_properties(text)
        return {
            "text": text,
            "tables": self._extract_tables_from_text(text, 1),
            "metadata": {"page_count": 1, **detected},
            "page_count": 1,
        }
    
    async def _process_fallback(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except:
            text = f"[Binary file: {os.path.basename(file_path)}]"
        return {
            "text": text,
            "tables": [],
            "metadata": {"page_count": 1},
            "page_count": 1,
        }
    
    def _extract_tables_from_text(self, text: str, page_num: int) -> List[Dict]:
        """Extract table-like structures from text using patterns."""
        tables = []
        lines = text.split('\n')
        table_rows = []
        
        for line in lines:
            numbers = re.findall(r'[\d,]+\.?\d*', line)
            if len(numbers) >= 2 and len(line.strip()) > 8:
                parts = [p.strip() for p in re.split(r'\s{2,}|\t|\|', line.strip()) if p.strip()]
                if len(parts) >= 2:
                    table_rows.append(parts)
            else:
                if len(table_rows) >= 2:
                    tables.append({
                        "table_index": len(tables),
                        "data": table_rows,
                        "source_page": page_num,
                    })
                table_rows = []
        
        if len(table_rows) >= 2:
            tables.append({
                "table_index": len(tables),
                "data": table_rows,
                "source_page": page_num,
            })
        
        return tables
    
    def _detect_document_properties(self, text: str) -> Dict[str, Any]:
        """Detect government level, state, financial year, document type from text."""
        properties = {}
        text_lower = text.lower()
        
        # Detect financial year
        fy_patterns = [
            r'(\d{4})[-–](\d{2,4})',
            r'financial\s+year\s+(\d{4})',
            r'budget\s+(\d{4})',
            r'FY\s*(\d{2,4})',
        ]
        for pattern in fy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    year1 = groups[0]
                    year2 = groups[1]
                    if len(year2) == 2:
                        properties["financial_year"] = f"{year1}-{year2}"
                    else:
                        properties["financial_year"] = f"{year1}-{year2[-2:]}"
                else:
                    y = groups[0]
                    if len(y) == 4:
                        properties["financial_year"] = f"{y}-{int(y[-2:])+1:02d}"
                    else:
                        properties["financial_year"] = y
                break
        
        if "financial_year" not in properties:
            properties["financial_year"] = "2024-25"
        
        # Detect state or union
        detected_state = None
        for state in self.INDIAN_STATES:
            if state.lower() in text_lower:
                detected_state = state
                break
        
        if detected_state:
            properties["government_level"] = "state"
            properties["state_name"] = detected_state
            properties["government_name"] = f"Government of {detected_state}"
        else:
            properties["government_level"] = "union"
            properties["government_name"] = "Government of India"
        
        # Detect document type
        doc_type_keywords = {
            "budget_speech": ["budget speech", "speech of", "hon'ble minister", "finance minister"],
            "annual_financial_statement": ["annual financial statement", "statement i", "consolidated fund"],
            "expenditure_budget": ["expenditure budget", "expenditure profile", "demand for grants"],
            "receipt_budget": ["receipt budget", "receipts budget", "revenue receipts"],
            "economic_survey": ["economic survey", "macroeconomic overview"],
            "fiscal_policy": ["fiscal policy", "frbm", "medium term fiscal"],
        }
        
        for doc_type, keywords in doc_type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                properties["document_type"] = doc_type
                break
        
        if "document_type" not in properties:
            properties["document_type"] = "budget_document"
        
        return properties

