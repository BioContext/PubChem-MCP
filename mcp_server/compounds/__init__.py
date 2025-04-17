"""
PubChem MCP server compounds module - handles compound structure, property and information functions.
"""

from mcp_server import FastMCP

# Import all tool modules with explicit assignment to keep them in scope
from . import structures
from . import properties

def register_compound_tools(mcp: FastMCP):
    """Register all compound tools with the MCP server"""
    # Inject the MCP instance into each module
    structures.mcp = mcp
    properties.mcp = mcp
    
    # Load modules (which will register their tools via the decorator)
    return {
        "structures": structures,
        "properties": properties
    }

from ..utils import pubchem_client, BASE_URL, PROPERTY_MAP
import urllib.parse
from typing import Dict, Any, Optional
import httpx

# Import tool functions from submodules
from .search import (
    search_compound_by_name,
    search_compound_by_smiles,
    search_compound_by_inchi,
    search_compound
)

from .details import (
    get_compound_details,
    get_compound_sdf,
    get_compound_smiles,
    get_compound_inchi,
    get_compound_mol,
    get_compound_image_url,
    get_compound_3d_coordinates,
    get_compound_conformers
)

from .properties import (
    get_compound_toxicity,
    get_compound_drug_interactions,
    get_compound_vendors
)

from .classifications import (
    get_compound_classification,
    get_compound_pharmacology,
    get_compound_targets
)

from .references import (
    get_compound_literature,
    get_compound_patents,
    get_compound_xrefs,
    get_compound_synonyms
)

# Re-export all functions
__all__ = [
    # Search functions
    'search_compound_by_name',
    'search_compound_by_smiles',
    'search_compound_by_inchi',
    'search_compound',
    
    # Details functions
    'get_compound_details',
    'get_compound_sdf',
    'get_compound_smiles',
    'get_compound_inchi',
    'get_compound_mol',
    'get_compound_image_url',
    'get_compound_3d_coordinates',
    'get_compound_conformers',
    
    # Properties functions
    'get_compound_toxicity',
    'get_compound_drug_interactions',
    'get_compound_vendors',
    
    # Classification functions
    'get_compound_classification',
    'get_compound_pharmacology',
    'get_compound_targets',
    
    # References functions
    'get_compound_literature',
    'get_compound_patents',
    'get_compound_xrefs',
    'get_compound_synonyms',
] 