import os
import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class ReportGenerator:
    """Generates downloadable, comprehensive budget intelligence reports (CSV, JSON, PDF)."""
    
    async def generate_report(
        self,
        workspace_id: str,
        analysis_data: Dict,
        format: str = "csv",
        sections: Optional[List[str]] = None,
        workspace_info: Dict = None,
    ) -> str:
        """Generate a complete budget analysis report."""
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_gov = ((workspace_info or {}).get("name") or "Budget").replace(" ", "_")
        safe_fy = ((workspace_info or {}).get("financial_year") or "FY").replace("-", "_")
        
        fmt = (format or "csv").lower()
        if fmt == "json":
            return await self._generate_json_report(workspace_id, analysis_data, safe_gov, safe_fy, timestamp)
        elif fmt in ("xlsx", "excel"):
            return await self._generate_excel_report(workspace_id, analysis_data, safe_gov, safe_fy, timestamp)
        elif fmt == "pdf":
            return await self._generate_pdf_report(workspace_id, analysis_data, safe_gov, safe_fy, timestamp, workspace_info)
        else:
            return await self._generate_csv_report(workspace_id, analysis_data, safe_gov, safe_fy, timestamp)

    async def _generate_csv_report(self, workspace_id: str, data: Dict, gov: str, fy: str, timestamp: str) -> str:
        filename = f"Budget_Report_{gov}_{fy}_{timestamp}.csv"
        filepath = os.path.join(settings.REPORTS_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["Budget Intelligence Platform - Official Economic Analysis Report"])
            w.writerow(["Government", gov.replace("_", " ")])
            w.writerow(["Financial Year", fy.replace("_", "-")])
            w.writerow(["Generated At", datetime.now().isoformat()])
            w.writerow([])
            
            # Overview
            overview = data.get("overview", {})
            w.writerow(["=== SECTION 1: MACRO FISCAL OVERVIEW (₹ Crore) ==="])
            w.writerow(["Metric", "Amount / Value", "Unit"])
            w.writerow(["Total Receipts", overview.get("total_receipts", "N/A"), "₹ Crore"])
            w.writerow(["Total Expenditure", overview.get("total_expenditure", "N/A"), "₹ Crore"])
            w.writerow(["Revenue Receipts", overview.get("revenue_receipts", "N/A"), "₹ Crore"])
            w.writerow(["Capital Receipts", overview.get("capital_receipts", "N/A"), "₹ Crore"])
            w.writerow(["Revenue Expenditure", overview.get("revenue_expenditure", "N/A"), "₹ Crore"])
            w.writerow(["Capital Expenditure (Asset Creation)", overview.get("capital_expenditure", "N/A"), "₹ Crore"])
            w.writerow(["Gross Fiscal Deficit", overview.get("fiscal_deficit", "N/A"), "₹ Crore"])
            w.writerow(["Fiscal Deficit (% of GDP/GSDP)", overview.get("fiscal_deficit_gdp_ratio", "N/A"), "%"])
            w.writerow(["Revenue Deficit", overview.get("revenue_deficit", "N/A"), "₹ Crore"])
            w.writerow(["Primary Deficit", overview.get("primary_deficit", "N/A"), "₹ Crore"])
            w.writerow([])
            
            # Executive Summary
            w.writerow(["=== SECTION 2: EXECUTIVE SUMMARY ==="])
            w.writerow([overview.get("executive_summary", "Detailed budget synthesis generated from uploaded documents.")])
            w.writerow([])
            
            # Highlights
            w.writerow(["=== SECTION 3: KEY BUDGET HIGHLIGHTS ==="])
            for h in overview.get("key_highlights", []):
                w.writerow([h])
            w.writerow([])
            
            # Receipts Breakdown
            receipts = data.get("receipts", {})
            w.writerow(["=== SECTION 4: GOVERNMENT RECEIPTS BREAKDOWN ==="])
            w.writerow(["Receipt Category", "Amount (₹ Crore)", "Share of Total (%)"])
            for comp in receipts.get("receipt_composition", []):
                w.writerow([comp.get("name", ""), comp.get("value", ""), comp.get("percentage", "")])
            
            tax = receipts.get("tax_revenue", {})
            if isinstance(tax, dict):
                w.writerow([])
                w.writerow(["Tax Head", "Collection (₹ Crore)"])
                for k, v in tax.items():
                    if isinstance(v, (int, float)) and k != "total":
                        w.writerow([k.replace("_", " ").title(), v])
            w.writerow([])
            
            # Expenditure Breakdown
            exp = data.get("expenditure", {})
            w.writerow(["=== SECTION 5: GOVERNMENT EXPENDITURE COMPOSITION ==="])
            w.writerow(["Expenditure Stream", "Amount (₹ Crore)", "Share of Total (%)"])
            for comp in exp.get("expenditure_composition", []):
                w.writerow([comp.get("name", ""), comp.get("value", ""), comp.get("percentage", "")])
            w.writerow([])
            
            # Sectors
            sectors = data.get("sectors", {}).get("sectors", [])
            if sectors:
                w.writerow(["=== SECTION 6: SECTOR-WISE ALLOCATIONS ==="])
                w.writerow(["Sector", "Allocation (₹ Crore)", "Percentage of Budget", "YoY Change (%)", "Key Schemes"])
                for s in sectors:
                    schemes_str = "; ".join(s.get("key_schemes", []) or [])
                    w.writerow([
                        s.get("sector_name") or s.get("name", ""),
                        s.get("allocation") or s.get("total_allocation", ""),
                        s.get("percentage") or s.get("percentage_of_total", ""),
                        s.get("yoy_change", ""),
                        schemes_str
                    ])
                w.writerow([])
            
            # Schemes
            schemes = data.get("schemes", {}).get("schemes", [])
            if schemes:
                w.writerow(["=== SECTION 7: SCHEMES & WELFARE MISSIONS ==="])
                w.writerow(["Scheme Name", "Sector", "Allocation (₹ Crore)", "Target Beneficiaries", "Objective"])
                for sc in schemes:
                    w.writerow([
                        sc.get("scheme_name") or sc.get("name", ""),
                        sc.get("sector", ""),
                        sc.get("allocation") or sc.get("current_allocation", ""),
                        sc.get("beneficiaries", ""),
                        sc.get("objective", "")
                    ])
                w.writerow([])
            
            # Macroeconomic Context
            macro = data.get("macroeconomic", {})
            if macro:
                w.writerow(["=== SECTION 8: MACROECONOMIC IMPACT & BENEFICIARY ANALYSIS ==="])
                w.writerow(["Citizen Demographic", "Impact Assessment", "Policy Driver"])
                for b in macro.get("who_benefits", []):
                    w.writerow([b.get("group", ""), b.get("impact", ""), b.get("explanation", "")])
        
        return filepath

    async def _generate_json_report(self, workspace_id: str, data: Dict, gov: str, fy: str, timestamp: str) -> str:
        filename = f"Budget_Report_{gov}_{fy}_{timestamp}.json"
        filepath = os.path.join(settings.REPORTS_DIR, filename)
        report_payload = {
            "platform": "Budget Intelligence Platform",
            "version": "1.0.0",
            "metadata": {
                "government": gov.replace("_", " "),
                "financial_year": fy.replace("_", "-"),
                "generated_at": datetime.now().isoformat(),
            },
            "analysis": data,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_payload, f, indent=2, ensure_ascii=False, default=str)
        return filepath

    async def _generate_excel_report(self, workspace_id: str, data: Dict, gov: str, fy: str, timestamp: str) -> str:
        try:
            import openpyxl
            filename = f"Budget_Report_{gov}_{fy}_{timestamp}.xlsx"
            filepath = os.path.join(settings.REPORTS_DIR, filename)
            wb = openpyxl.Workbook()
            
            ws1 = wb.active
            ws1.title = "Overview"
            ws1.append(["Budget Intelligence Official Report"])
            ws1.append(["Government", gov.replace("_", " ")])
            ws1.append(["Financial Year", fy.replace("_", "-")])
            ws1.append([])
            
            overview = data.get("overview", {})
            ws1.append(["Metric", "Value", "Unit"])
            ws1.append(["Total Expenditure", overview.get("total_expenditure"), "₹ Crore"])
            ws1.append(["Total Receipts", overview.get("total_receipts"), "₹ Crore"])
            ws1.append(["Revenue Receipts", overview.get("revenue_receipts"), "₹ Crore"])
            ws1.append(["Capital Receipts", overview.get("capital_receipts"), "₹ Crore"])
            ws1.append(["Revenue Expenditure", overview.get("revenue_expenditure"), "₹ Crore"])
            ws1.append(["Capital Expenditure", overview.get("capital_expenditure"), "₹ Crore"])
            ws1.append(["Fiscal Deficit", overview.get("fiscal_deficit"), "₹ Crore"])
            ws1.append(["Fiscal Deficit / GDP", overview.get("fiscal_deficit_gdp_ratio"), "%"])
            
            # Sectors sheet
            ws2 = wb.create_sheet("Sectors")
            ws2.append(["Sector", "Allocation (₹ Cr)", "Share (%)", "YoY Change (%)"])
            for s in data.get("sectors", {}).get("sectors", []):
                ws2.append([
                    s.get("sector_name") or s.get("name", ""),
                    s.get("allocation") or s.get("total_allocation", 0),
                    s.get("percentage") or s.get("percentage_of_total", 0),
                    s.get("yoy_change", 0)
                ])
            
            # Schemes sheet
            ws3 = wb.create_sheet("Schemes")
            ws3.append(["Scheme Name", "Sector", "Allocation (₹ Cr)", "Objective"])
            for sc in data.get("schemes", {}).get("schemes", []):
                ws3.append([
                    sc.get("scheme_name") or sc.get("name", ""),
                    sc.get("sector", ""),
                    sc.get("allocation") or sc.get("current_allocation", 0),
                    sc.get("objective", "")
                ])
            
            wb.save(filepath)
            return filepath
        except Exception as e:
            logger.warning(f"Excel generation fallback to CSV: {e}")
            return await self._generate_csv_report(workspace_id, data, gov, fy, timestamp)

    async def _generate_pdf_report(self, workspace_id: str, data: Dict, gov: str, fy: str, timestamp: str, info: Dict) -> str:
        """Generate PDF report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            filename = f"Budget_Report_{gov}_{fy}_{timestamp}.pdf"
            filepath = os.path.join(settings.REPORTS_DIR, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#0f172a"),
                spaceAfter=6,
            )
            
            sub_style = ParagraphStyle(
                'ReportSub',
                parent=styles['Normal'],
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#475569"),
                spaceAfter=15,
            )
            
            h2_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#1e293b"),
                spaceBefore=12,
                spaceAfter=8,
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#334155"),
                spaceAfter=6,
            )
            
            def _fmt_val(v, default=0):
                if v is None:
                    return f"{default:,}"
                if isinstance(v, (int, float)):
                    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"
                import re
                try:
                    cleaned = float(re.sub(r'[^\d.-]', '', str(v)))
                    return f"{cleaned:,.0f}" if cleaned.is_integer() else f"{cleaned:,.2f}"
                except:
                    return str(v or default)

            elements = []
            
            elements.append(Paragraph(f"Budget Intelligence Report: {gov.replace('_', ' ')}", title_style))
            elements.append(Paragraph(f"Financial Year: {fy.replace('_', '-')} | Generated: {datetime.now().strftime('%d %B %Y')}", sub_style))
            elements.append(Spacer(1, 10))
            
            overview = data.get("overview", {})
            elements.append(Paragraph("1. Executive Summary & Fiscal Stance", h2_style))
            elements.append(Paragraph(overview.get("executive_summary", "Comprehensive analysis."), body_style))
            elements.append(Spacer(1, 10))
            
            elements.append(Paragraph("2. Key Fiscal Indicators", h2_style))
            table_data = [
                ["Indicator", "Amount / Ratio", "Classification"],
                ["Total Expenditure", f"₹{_fmt_val(overview.get('total_expenditure'))} Cr", "Budget Size"],
                ["Total Receipts", f"₹{_fmt_val(overview.get('total_receipts'))} Cr", "Total Inflows"],
                ["Revenue Expenditure", f"₹{_fmt_val(overview.get('revenue_expenditure'))} Cr", "Committed & Recurring"],
                ["Capital Expenditure", f"₹{_fmt_val(overview.get('capital_expenditure'))} Cr", "Asset Creation"],
                ["Gross Fiscal Deficit", f"₹{_fmt_val(overview.get('fiscal_deficit'))} Cr", f"{overview.get('fiscal_deficit_gdp_ratio', 4.9)}% of GDP"],
                ["Revenue Deficit", f"₹{_fmt_val(overview.get('revenue_deficit'))} Cr", "Consumption Gap"],
            ]
            
            t = Table(table_data, colWidths=[200, 150, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))
            
            elements.append(Paragraph("3. Sector-Wise Allocations", h2_style))
            sectors = data.get("sectors", {}).get("sectors", [])[:10]
            sec_table_data = [["Sector Name", "Allocation (₹ Cr)", "Share (%)"]]
            for s in sectors:
                alloc = s.get('allocation') or s.get('total_allocation', 0)
                pct = s.get('percentage') or s.get('percentage_of_total', 0)
                sec_table_data.append([
                    str(s.get("sector_name") or s.get("name", ""))[:35],
                    f"₹{_fmt_val(alloc)}",
                    f"{pct}%"
                ])
            sec_table = Table(sec_table_data, colWidths=[240, 130, 130])
            sec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            elements.append(sec_table)
            
            doc.build(elements)
            return filepath
        except Exception as e:
            logger.warning(f"PDF generation fallback to CSV: {e}")
            return await self._generate_csv_report(workspace_id, data, gov, fy, timestamp)

