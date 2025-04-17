"""
Tests for PubChem structure search endpoints.
"""

import pytest
from pubchem_mcp_server import (
    search_by_substructure,
    search_by_similarity,
    search_by_exact_structure
)

# Test data
TEST_SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
TEST_SUBSTRUCTURE = "C1=CC=CC=C1"  # Benzene ring
TEST_INVALID_SMILES = "XXX"

@pytest.mark.asyncio
async def test_search_by_substructure():
    """Test substructure search functionality."""
    result = await search_by_substructure(TEST_SUBSTRUCTURE)
    assert "Compound" in result
    assert "PubChem CID" in result
    assert "Formula" in result
    assert "Weight" in result

@pytest.mark.asyncio
async def test_search_by_similarity():
    """Test similarity search functionality."""
    result = await search_by_similarity(TEST_SMILES, threshold=0.8)
    assert "Compound" in result
    assert "PubChem CID" in result
    assert "Formula" in result
    assert "Weight" in result

@pytest.mark.asyncio
async def test_search_by_exact_structure():
    """Test exact structure search functionality."""
    result = await search_by_exact_structure(TEST_SMILES)
    assert "Exact Structure Match" in result
    assert "Name" in result
    assert "PubChem CID" in result
    assert "Formula" in result
    assert "Weight" in result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid SMILES for substructure search
    result = await search_by_substructure(TEST_INVALID_SMILES)
    assert "Error" in result
    
    # Test invalid SMILES for similarity search
    result = await search_by_similarity(TEST_INVALID_SMILES)
    assert "Error" in result
    
    # Test invalid SMILES for exact structure search
    result = await search_by_exact_structure(TEST_INVALID_SMILES)
    assert "Error" in result 