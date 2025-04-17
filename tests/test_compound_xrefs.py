"""
Tests for PubChem compound cross-reference endpoints.
"""

import pytest
from pubchem_mcp_server import (
    get_compound_xrefs,
    get_compound_synonyms
)

# Test data
TEST_CID = "2244"  # Aspirin

@pytest.mark.asyncio
async def test_get_compound_xrefs():
    """Test retrieving compound cross-references."""
    result = await get_compound_xrefs(TEST_CID)
    assert "Cross-References for CID" in result
    
    # Should have at least one of these common database references for Aspirin
    assert any(db in result for db in [
        "ChEBI", "DrugBank", "KEGG", "CAS", "ChEMBL"
    ])
    
    # Check for IDs in the result
    assert any(id_prefix in result for id_prefix in [
        "CHEMBL", "DB", "CHEBI:", "C0"  # Common ID prefixes
    ])

@pytest.mark.asyncio
async def test_get_compound_synonyms():
    """Test retrieving compound synonyms."""
    result = await get_compound_synonyms(TEST_CID)
    assert "Synonyms for CID" in result
    
    # Should have common synonym names for Aspirin
    assert any(name in result for name in [
        "Aspirin", "Acetylsalicylic acid", "ASA", "2-(acetyloxy)benzoic acid"
    ])

@pytest.mark.asyncio
async def test_get_compound_synonyms_limit():
    """Test limiting the number of synonyms."""
    result_default = await get_compound_synonyms(TEST_CID)
    result_limited = await get_compound_synonyms(TEST_CID, max_synonyms=3)
    
    # The limited result should contain fewer synonyms
    assert len(result_limited) < len(result_default)
    
    # Count the number of lines starting with a digit (synonym entries)
    synonym_lines = [line for line in result_limited.split('\n') if line.strip().startswith(('1.', '2.', '3.'))]
    assert len(synonym_lines) <= 3
    
    # Should mention the limit
    if "Showing" in result_limited:
        assert "Showing 3 of" in result_limited

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid CID
    result = await get_compound_xrefs("999999999")
    assert "No cross-references" in result or "Error" in result
    
    result = await get_compound_synonyms("999999999")
    assert "No synonyms" in result or "Error" in result 