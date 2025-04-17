"""
Tests for PubChem substance endpoints.
"""

import pytest
from pubchem_mcp_server import (
    search_substance_by_name,
    get_substance_details,
    get_substance_sdf,
    get_substance_synonyms
)

# Test substances
TEST_SUBSTANCE_NAME = "aspirin"
TEST_SID = "347827282"  # Example SID for aspirin

@pytest.mark.asyncio
async def test_search_substance_by_name():
    """Test substance search by name functionality."""
    result = await search_substance_by_name(TEST_SUBSTANCE_NAME)
    assert "Substance Details" in result
    assert "SID" in result
    assert "Name" in result
    assert "Source" in result

@pytest.mark.asyncio
async def test_get_substance_details():
    """Test getting substance details."""
    result = await get_substance_details(TEST_SID)
    assert "Substance Details" in result
    assert "SID" in result
    assert "Name" in result
    assert "Source" in result
    assert "Depositor" in result

@pytest.mark.asyncio
async def test_get_substance_sdf():
    """Test getting substance SDF format."""
    result = await get_substance_sdf(TEST_SID)
    assert "V3000" in result or "V2000" in result  # SDF format markers
    assert "M  END" in result  # SDF end marker

@pytest.mark.asyncio
async def test_get_substance_synonyms():
    """Test getting substance synonyms."""
    result = await get_substance_synonyms(TEST_SID)
    assert "Synonyms" in result
    assert "SID" in result
    assert "Count" in result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid substance name
    result = await search_substance_by_name("invalid_substance_name_xyz")
    assert "No substances found" in result
    
    # Test invalid SID
    result = await get_substance_details("999999999")
    assert "Error" in result
    
    # Test invalid SID for SDF
    result = await get_substance_sdf("999999999")
    assert "Error" in result
    
    # Test invalid SID for synonyms
    result = await get_substance_synonyms("999999999")
    assert "Error" in result 