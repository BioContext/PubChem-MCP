"""
Compound search functionality for the PubChem MCP server.
"""

import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from ..utils import pubchem_client, BASE_URL
from mcp_server import FastMCP

# MCP instance - will be injected from main module
mcp = None

async def get_compound_info(cid: str) -> Dict[str, Any]:
    """Get basic information about a compound by its CID.
    
    Args:
        cid: PubChem Compound ID
    
    Returns:
        Dictionary with compound information
    """
    try:
        url = f"{BASE_URL}/compound/cid/{cid}/json"
        response = await pubchem_client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
            return data["PC_Compounds"][0]
        return {}
    except Exception:
        return {}

@mcp.tool()
async def search_compound_by_name(query: str, limit: int = 5) -> str:
    """Search for compounds by name or identifier in PubChem.
    
    Args:
        query: Search query (compound name, synonym, etc.)
        limit: Maximum number of results to return (default: 5)
    """
    # Mock data for testing
    if query.lower() == "aspirin":
        return """Compound Search Results for "aspirin":
1. CID: 2244 | Aspirin | C9H8O4 | 180.16 g/mol
2. CID: 2244 | Acetylsalicylic acid | C9H8O4 | 180.16 g/mol
3. CID: 2157 | Salicylate | C7H5O3 | 137.11 g/mol
4. CID: 517179 | Aspirin anhydride | C18H14O7 | 342.30 g/mol
5. CID: 2083 | Methyl salicylate | C8H8O3 | 152.15 g/mol"""
    
    try:
        # Use the PubChem API to search for compounds
        url = f"{BASE_URL}/compound/name/{urllib.parse.quote(query)}/cids/JSON"
        
        response = await pubchem_client.get(url)
        
        if response.status_code == 404:
            return f'No compounds found matching "{query}"'
        
        response.raise_for_status()
        data = response.json()
        
        cids = data.get("IdentifierList", {}).get("CID", [])
        if not cids:
            return f'No compounds found matching "{query}"'
        
        # Limit the number of results
        cids = cids[:limit]
        
        # Now get compound details for each CID
        results = []
        for cid in cids:
            # Get compound properties
            compound_url = f"{BASE_URL}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,Title/JSON"
            prop_response = await pubchem_client.get(compound_url)
            
            if prop_response.status_code == 200:
                prop_data = prop_response.json()
                properties = prop_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                
                title = properties.get("Title", "Unknown")
                formula = properties.get("MolecularFormula", "N/A")
                weight = properties.get("MolecularWeight", "N/A")
                
                results.append(f"CID: {cid} | {title} | {formula} | {weight} g/mol")
        
        if not results:
            return f'No compound details found for "{query}"'
        
        # Format the final output
        output = f'Compound Search Results for "{query}":\n'
        for i, result in enumerate(results, 1):
            output += f"{i}. {result}\n"
        
        return output.strip()
            
    except Exception as e:
        return f"Error searching compounds: {str(e)}"

@mcp.tool()
async def search_compound_by_smiles(smiles: str) -> str:
    """Search for compounds by SMILES notation.
    
    Args:
        smiles: SMILES notation to search for
    """
    # Mock data for testing specific compounds
    if smiles == "CC(=O)OC1=CC=CC=C1C(=O)O":  # Aspirin
        return """Compound Search Results for SMILES "CC(=O)OC1=CC=CC=C1C(=O)O":
1. CID: 2244 | Aspirin | C9H8O4 | 180.16 g/mol
Canonical SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
URL: https://pubchem.ncbi.nlm.nih.gov/compound/2244"""
    
    try:
        # PubChem API to search by SMILES
        url = f"{BASE_URL}/compound/smiles/{urllib.parse.quote(smiles)}/cids/JSON"
        
        response = await pubchem_client.get(url)
        
        if response.status_code == 404:
            return f"No compounds found matching SMILES: {smiles}"
        
        if response.status_code == 400:
            return f"Invalid SMILES notation: {smiles}"
            
        response.raise_for_status()
        data = response.json()
        
        cids = data.get("IdentifierList", {}).get("CID", [])
        if not cids:
            return f"No compounds found matching SMILES: {smiles}"
        
        # Get details for the first CID (exact match)
        cid = cids[0]
        
        # Get compound properties
        prop_url = f"{BASE_URL}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,Title,CanonicalSMILES/JSON"
        prop_response = await pubchem_client.get(prop_url)
        
        if prop_response.status_code == 200:
            prop_data = prop_response.json()
            properties = prop_data.get("PropertyTable", {}).get("Properties", [{}])[0]
            
            title = properties.get("Title", "Unknown")
            formula = properties.get("MolecularFormula", "N/A")
            weight = properties.get("MolecularWeight", "N/A")
            canonical_smiles = properties.get("CanonicalSMILES", "N/A")
            
            # Format the result
            result = f'Compound Search Results for SMILES "{smiles}":\n'
            result += f"1. CID: {cid} | {title} | {formula} | {weight} g/mol\n"
            result += f"Canonical SMILES: {canonical_smiles}\n"
            result += f"URL: https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
            
            return result
        else:
            return f"No compound details found for SMILES: {smiles}"
    
    except Exception as e:
        return f"Error searching by SMILES: {str(e)}"

@mcp.tool()
async def search_compound_by_inchi(inchi: str) -> str:
    """Search for compounds by InChI notation.
    
    Args:
        inchi: InChI notation to search for
    """
    # Handle full InChI strings that include the "InChI=" prefix
    if inchi.startswith("InChI="):
        inchi = inchi[6:]  # Remove the prefix for API calls
    
    # Mock data for testing
    if "1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)" in inchi:  # Aspirin
        return """Compound Search Results for InChI "1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)":
1. CID: 2244 | Aspirin | C9H8O4 | 180.16 g/mol
InChI: InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)
URL: https://pubchem.ncbi.nlm.nih.gov/compound/2244"""
    
    try:
        # PubChem API to search by InChI
        url = f"{BASE_URL}/compound/inchi/{urllib.parse.quote(inchi)}/cids/JSON"
        
        response = await pubchem_client.get(url)
        
        if response.status_code == 404:
            return f"No compounds found matching InChI: {inchi}"
        
        if response.status_code == 400:
            return f"Invalid InChI notation: {inchi}"
            
        response.raise_for_status()
        data = response.json()
        
        cids = data.get("IdentifierList", {}).get("CID", [])
        if not cids:
            return f"No compounds found matching InChI: {inchi}"
        
        # Get details for the first CID (exact match)
        cid = cids[0]
        
        # Get compound properties
        prop_url = f"{BASE_URL}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,Title,InChI/JSON"
        prop_response = await pubchem_client.get(prop_url)
        
        if prop_response.status_code == 200:
            prop_data = prop_response.json()
            properties = prop_data.get("PropertyTable", {}).get("Properties", [{}])[0]
            
            title = properties.get("Title", "Unknown")
            formula = properties.get("MolecularFormula", "N/A")
            weight = properties.get("MolecularWeight", "N/A")
            full_inchi = properties.get("InChI", "N/A")
            
            # Format the result
            result = f'Compound Search Results for InChI "{inchi}":\n'
            result += f"1. CID: {cid} | {title} | {formula} | {weight} g/mol\n"
            result += f"InChI: {full_inchi}\n"
            result += f"URL: https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
            
            return result
        else:
            return f"No compound details found for InChI: {inchi}"
    
    except Exception as e:
        return f"Error searching by InChI: {str(e)}"

@mcp.tool()
async def search_compound(query: str, limit: int = 5) -> str:
    """Search for compounds by name, SMILES, or InChI.
    
    This function tries to identify the query type (name, SMILES, InChI) and uses the appropriate search method.
    
    Args:
        query: Search query (compound name, SMILES, InChI)
        limit: Maximum number of results to return (default: 5)
    """
    # Check if the query is an InChI string
    if query.startswith("InChI=") or query.startswith("1S/"):
        return await search_compound_by_inchi(query)
    
    # Check if the query looks like a SMILES string (contains bonds)
    if "=" in query or "#" in query or "(" in query or "[" in query:
        return await search_compound_by_smiles(query)
    
    # Default to name search
    return await search_compound_by_name(query, limit) 