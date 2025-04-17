"""
Tests for PubChem bioassay endpoints.
"""

import pytest
from pubchem_mcp_server import (
    search_bioassays,
    get_bioassay_details,
    get_bioassay_results
)

# Test data
TEST_BIOASSAY_QUERY = "aspirin"
TEST_AID = "1000"  # Example AID
TEST_CID = "2244"  # CID for aspirin

@pytest.mark.asyncio
async def test_search_bioassays():
    """Test bioassay search functionality."""
    result = await search_bioassays(TEST_BIOASSAY_QUERY)
    assert "Bioassay Details" in result
    assert "AID" in result
    assert "Name" in result
    assert "Description" in result

@pytest.mark.asyncio
async def test_get_bioassay_details():
    """Test getting bioassay details."""
    result = await get_bioassay_details(TEST_AID)
    assert "Bioassay Details" in result
    assert "AID" in result
    assert "Name" in result
    assert "Target" in result
    assert "Protocol" in result

@pytest.mark.asyncio
async def test_get_bioassay_results():
    """Test getting bioassay results."""
    result = await get_bioassay_results(TEST_AID)
    assert "Result" in result
    assert "Outcome" in result
    assert "Score" in result
    assert "Activity" in result

@pytest.mark.asyncio
async def test_get_bioassay_results_with_compound():
    """Test getting bioassay results filtered by compound."""
    result = await get_bioassay_results(TEST_AID, TEST_CID)
    assert "Result" in result
    assert "Outcome" in result
    assert "Score" in result
    assert "Activity" in result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid bioassay query
    result = await search_bioassays("invalid_bioassay_xyz")
    assert "No bioassays found" in result
    
    # Test invalid AID
    result = await get_bioassay_details("999999999")
    assert "Error" in result
    
    # Test invalid AID for results
    result = await get_bioassay_results("999999999")
    assert "Error" in result 