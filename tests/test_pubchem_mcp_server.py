"""
Tests for the PubChem MCP server implementation.
"""

import pytest
from pubchem_mcp_server import (
    search_compound_by_name,
    search_compound_by_smiles,
    search_compound_by_inchi,
    get_compound_details,
    get_compound_sdf,
    get_compound_smiles,
    get_compound_inchi
)

# Test compounds
TEST_COMPOUND_NAME = "aspirin"
TEST_SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin SMILES
TEST_INCHI = "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"  # Aspirin InChI
TEST_CID = "2244"  # Aspirin CID

@pytest.mark.asyncio
async def test_search_compound_by_name():
    """Test compound search by name functionality."""
    result = await search_compound_by_name(TEST_COMPOUND_NAME)
    assert "Compound" in result
    assert "PubChem CID" in result
    assert "Formula" in result
    assert "Weight" in result

@pytest.mark.asyncio
async def test_search_compound_by_smiles():
    """Test compound search by SMILES functionality."""
    result = await search_compound_by_smiles(TEST_SMILES)
    assert "Compound Details" in result
    assert "CID" in result
    assert "Name" in result

@pytest.mark.asyncio
async def test_search_compound_by_inchi():
    """Test compound search by InChI functionality."""
    result = await search_compound_by_inchi(TEST_INCHI)
    assert "Compound Details" in result
    assert "CID" in result
    assert "Name" in result

@pytest.mark.asyncio
async def test_get_compound_details():
    """Test getting compound details."""
    result = await get_compound_details(TEST_CID)
    assert "Compound Details" in result
    assert "Name" in result
    assert "Formula" in result
    assert "Weight" in result
    assert "LogP" in result

@pytest.mark.asyncio
async def test_get_compound_sdf():
    """Test getting compound SDF format."""
    result = await get_compound_sdf(TEST_CID)
    assert "V3000" in result or "V2000" in result  # SDF format markers
    assert "M  END" in result  # SDF end marker

@pytest.mark.asyncio
async def test_get_compound_smiles():
    """Test getting compound SMILES."""
    result = await get_compound_smiles(TEST_CID)
    assert "SMILES" in result
    assert TEST_CID in result
    assert TEST_SMILES in result

@pytest.mark.asyncio
async def test_get_compound_inchi():
    """Test getting compound InChI."""
    result = await get_compound_inchi(TEST_CID)
    assert "InChI" in result
    assert TEST_CID in result
    assert TEST_INCHI in result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid compound name
    result = await search_compound_by_name("invalid_compound_name_xyz")
    assert "No compounds found" in result
    
    # Test invalid SMILES
    result = await search_compound_by_smiles("invalid_smiles")
    assert "No compounds found" in result
    
    # Test invalid InChI
    result = await search_compound_by_inchi("invalid_inchi")
    assert "No compounds found" in result
    
    # Test invalid CID
    result = await get_compound_details("999999999")
    assert "Error" in result 