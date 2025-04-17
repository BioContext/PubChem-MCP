"""
Tests for PubChem literature information endpoints.
"""

import pytest
from pubchem_mcp_server import (
    get_compound_literature,
    get_compound_patents
)

# Test data
TEST_CID = "2244"  # Aspirin

@pytest.mark.asyncio
async def test_get_compound_literature():
    """Test retrieving compound literature references."""
    result = await get_compound_literature(TEST_CID)
    assert "PubMed Citations for CID" in result
    assert "PMID:" in result
    assert "https://pubmed.ncbi.nlm.nih.gov/" in result

@pytest.mark.asyncio
async def test_get_compound_literature_limit():
    """Test limiting the number of literature references."""
    result_default = await get_compound_literature(TEST_CID)
    result_limited = await get_compound_literature(TEST_CID, max_results=3)
    
    # The limited result should be shorter than the default
    assert len(result_limited) < len(result_default)
    assert "PMID:" in result_limited
    
    # Should only have 3 PMID entries
    pmid_count = result_limited.count("PMID:")
    assert pmid_count <= 3

@pytest.mark.asyncio
async def test_get_compound_patents():
    """Test retrieving compound patent information."""
    result = await get_compound_patents(TEST_CID)
    assert "Patents for CID" in result
    assert "US" in result  # Most patents contain US in their ID

@pytest.mark.asyncio
async def test_get_compound_patents_limit():
    """Test limiting the number of patent references."""
    result_default = await get_compound_patents(TEST_CID)
    result_limited = await get_compound_patents(TEST_CID, max_results=3)
    
    # The limited result should be shorter than the default
    assert len(result_limited) < len(result_default)
    
    # Count the number of lines starting with a digit (patent entries)
    patent_lines = [line for line in result_limited.split('\n') if line.strip().startswith(('1.', '2.', '3.'))]
    assert len(patent_lines) <= 3

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid CID
    result = await get_compound_literature("999999999")
    assert "No literature references" in result or "Error" in result
    
    result = await get_compound_patents("999999999")
    assert "No patent references" in result or "Error" in result 