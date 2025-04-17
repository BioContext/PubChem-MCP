"""
Tests for PubChem compound classification endpoints.
"""

import pytest
from pubchem_mcp_server import (
    get_compound_classification,
    get_compound_pharmacology,
    get_compound_targets
)

# Test data
TEST_CID = "2244"  # Aspirin

@pytest.mark.asyncio
async def test_get_compound_classification():
    """Test retrieving compound classification data."""
    result = await get_compound_classification(TEST_CID)
    assert "Classification for CID" in result
    assert "Acetylsalicylic Acid" in result or "Aspirin" in result
    assert "→" in result  # Check for hierarchy separator

@pytest.mark.asyncio
async def test_get_compound_pharmacology():
    """Test retrieving compound pharmacological action data."""
    result = await get_compound_pharmacology(TEST_CID)
    assert "Pharmacological Actions for CID" in result
    assert "Anti-Inflammatory" in result or "Cyclooxygenase Inhibitors" in result
    assert "•" in result  # Check for bullet points

@pytest.mark.asyncio
async def test_get_compound_targets():
    """Test retrieving compound target data."""
    result = await get_compound_targets(TEST_CID)
    assert "Biological Targets for CID" in result
    assert "Prostaglandin" in result or "Cyclooxygenase" in result
    assert "•" in result  # Check for bullet points

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid CID
    result = await get_compound_classification("999999999")
    assert "No classification data" in result or "Error" in result
    
    result = await get_compound_pharmacology("999999999")
    assert "No pharmacological action" in result or "Error" in result
    
    result = await get_compound_targets("999999999")
    assert "No target data" in result or "Error" in result 