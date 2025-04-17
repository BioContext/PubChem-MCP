"""
Tests for PubChem compound format endpoints.
"""

import pytest
from pubchem_mcp_server import (
    get_compound_mol,
    get_compound_image_url,
    get_compound_3d_coordinates,
    get_compound_conformers
)

# Test data
TEST_CID = "2244"  # Aspirin

@pytest.mark.asyncio
async def test_get_compound_mol():
    """Test retrieving compound MOL format."""
    result = await get_compound_mol(TEST_CID)
    # Check for MOL format indicators
    assert "V2000" in result or "V3000" in result
    assert "M  END" in result
    
    # Check for some atoms that should be in Aspirin
    assert " C " in result
    assert " O " in result

@pytest.mark.asyncio
async def test_get_compound_image_url():
    """Test retrieving compound image URLs."""
    # Test 2D image URL
    result_2d = await get_compound_image_url(TEST_CID, image_type="2d")
    assert "Image URL for CID" in result_2d
    assert "imgsrv.fcgi" in result_2d
    
    # Test 3D image URL
    result_3d = await get_compound_image_url(TEST_CID, image_type="3d")
    assert "Image URL for CID" in result_3d
    assert "img3d.cgi" in result_3d
    
    # Test invalid image type
    result_invalid = await get_compound_image_url(TEST_CID, image_type="invalid")
    assert "Invalid image type" in result_invalid

@pytest.mark.asyncio
async def test_get_compound_3d_coordinates():
    """Test retrieving compound 3D coordinates."""
    result = await get_compound_3d_coordinates(TEST_CID)
    assert "3D Coordinates for CID" in result
    
    # Check for coordinate table headers
    assert "Atom" in result
    assert "X" in result
    assert "Y" in result
    assert "Z" in result
    
    # Check for some atoms that should be in Aspirin
    assert "C\t" in result or "C " in result
    assert "O\t" in result or "O " in result

@pytest.mark.asyncio
async def test_get_compound_conformers():
    """Test retrieving compound conformer information."""
    result = await get_compound_conformers(TEST_CID)
    assert "Conformers for CID" in result
    assert "Conformer ID:" in result
    assert "URL:" in result
    assert "https://pubchem.ncbi.nlm.nih.gov/conformer/" in result

@pytest.mark.asyncio
async def test_get_compound_conformers_limit():
    """Test limiting the number of conformers."""
    result_default = await get_compound_conformers(TEST_CID)
    result_limited = await get_compound_conformers(TEST_CID, max_conformers=2)
    
    # The limited result should contain fewer conformers
    assert len(result_limited) < len(result_default)
    
    # Should only have 2 conformer entries
    conformer_lines = [line for line in result_limited.split('\n') if "Conformer ID:" in line]
    assert len(conformer_lines) <= 2

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid CID
    result = await get_compound_mol("999999999")
    assert "No MOL data" in result or "Error" in result
    
    result = await get_compound_3d_coordinates("999999999")
    assert "No 3D data" in result or "Error" in result
    
    result = await get_compound_conformers("999999999")
    assert "No conformer data" in result or "Error" in result 