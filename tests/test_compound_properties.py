"""
Tests for PubChem additional compound property endpoints.
"""

import pytest
from pubchem_mcp_server import (
    get_compound_toxicity,
    get_compound_drug_interactions,
    get_compound_vendors
)

# Test data
TEST_CID = "2244"  # Aspirin

@pytest.mark.asyncio
async def test_get_compound_toxicity():
    """Test retrieving compound toxicity data."""
    result = await get_compound_toxicity(TEST_CID)
    assert "Toxicity Information for CID" in result
    assert "GHS" in result or "HSDB" in result or "Warning" in result

@pytest.mark.asyncio
async def test_get_compound_drug_interactions():
    """Test retrieving compound drug interaction data."""
    result = await get_compound_drug_interactions(TEST_CID)
    assert "Drug Information for CID" in result
    assert "DrugBank" in result
    
    # Should have DrugBank IDs for Aspirin
    assert "DB" in result
    assert "https://go.drugbank.com/drugs/" in result

@pytest.mark.asyncio
async def test_get_compound_vendors():
    """Test retrieving compound vendor information."""
    result = await get_compound_vendors(TEST_CID)
    assert "Vendor Information for CID" in result
    
    # Should have some product IDs for common vendors
    assert "Product ID:" in result
    
    # At least one of these common vendors should be found for Aspirin
    assert any(vendor in result for vendor in [
        "Sigma-Aldrich", "Cayman", "ChemicalBook", "Alfa", "MolPort", "Mcule"
    ])

@pytest.mark.asyncio
async def test_get_compound_vendors_limit():
    """Test limiting the number of vendors."""
    result_default = await get_compound_vendors(TEST_CID)
    result_limited = await get_compound_vendors(TEST_CID, max_vendors=2)
    
    # The limited result should contain fewer vendors
    assert len(result_limited) < len(result_default)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid CID
    result = await get_compound_toxicity("999999999")
    assert "No toxicity information" in result or "Error" in result
    
    result = await get_compound_drug_interactions("999999999")
    assert "No drug interaction information" in result or "Error" in result
    
    result = await get_compound_vendors("999999999")
    assert "No vendor information" in result or "Error" in result 