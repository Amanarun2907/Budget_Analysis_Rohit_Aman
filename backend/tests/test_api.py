import pytest
import os
import sys

# Ensure backend path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.document_processing.processor import DocumentProcessor
from app.services.analysis.budget_agents import BudgetAgentSystem

def test_document_processor_detection():
    processor = DocumentProcessor()
    text = "The Government of Uttar Pradesh presents the Annual Financial Statement for Budget 2024-25 in the Vidhan Sabha."
    props = processor._detect_document_properties(text)
    
    assert props["government_level"] == "state"
    assert props["state_name"] == "Uttar Pradesh"
    assert props["financial_year"] == "2024-25"

def test_union_budget_detection():
    processor = DocumentProcessor()
    text = "Speech of Minister of Finance on presenting the Union Budget 2024-2025 in Parliament."
    props = processor._detect_document_properties(text)
    
    assert props["government_level"] == "union"
    assert props["financial_year"] == "2024-25"

def test_reconciliation_logic():
    agent_system = BudgetAgentSystem()
    results = {}
    metadata = {
        "government_name": "Government of India",
        "financial_year": "2024-25",
        "government_level": "union",
    }
    agent_system._reconcile_and_fill_fallbacks(results, metadata, "Total Expenditure: ₹48,20,512 crore")
    
    overview = results["overview"]
    assert overview["government_name"] == "Government of India"
    assert overview["total_expenditure"] == 4820512.0
    assert overview["revenue_expenditure"] > 0
    assert overview["capital_expenditure"] > 0
    assert "receipt_composition" in results["receipts"]
    assert "sectors" in results["sectors"]
    assert len(results["sectors"]["sectors"]) > 0

if __name__ == "__main__":
    test_document_processor_detection()
    test_union_budget_detection()
    test_reconciliation_logic()
    print("All unit tests passed successfully!")

