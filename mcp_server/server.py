"""
PubChem MCP server implementation.
"""

import json
from typing import Any, Dict, List, Optional, Union

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Initialize the MCP server
app = FastMCP("pubchem")

# Constants
PUBCHEM_REST_API = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUBCHEM_VIEW_API = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
USER_AGENT = "PubChem-MCP/0.1.0"

# Helper functions
async def make_pubchem_request(url: str) -> Dict[str, Any]:
    """Make a request to the PubChem API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "message": str(e)}
        except httpx.RequestError as e:
            return {"error": "Request error", "message": str(e)}
        except Exception as e:
            return {"error": "Unexpected error", "message": str(e)}

# MCP Tools
@app.tool("search_compound")
async def search_compound(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search for compounds by name, CID, or other identifiers.
    
    Args:
        query: The search query (compound name, CID, SMILES, etc.)
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        Dictionary with search results
    """
    url = f"{PUBCHEM_REST_API}/compound/name/{query}/cids/JSON?MaxRecords={max_results}"
    response = await make_pubchem_request(url)
    
    if "error" in response:
        return response
    
    # Process results
    compounds = []
    if "IdentifierList" in response and "CID" in response["IdentifierList"]:
        for cid in response["IdentifierList"]["CID"]:
            # Get basic info for each compound
            info_url = f"{PUBCHEM_REST_API}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            info = await make_pubchem_request(info_url)
            
            if "error" not in info and "PropertyTable" in info:
                props = info["PropertyTable"]["Properties"][0] if info["PropertyTable"]["Properties"] else {}
                compounds.append({
                    "CID": cid,
                    "IUPACName": props.get("IUPACName", "Unknown"),
                    "MolecularFormula": props.get("MolecularFormula", ""),
                    "MolecularWeight": props.get("MolecularWeight", ""),
                    "CanonicalSMILES": props.get("CanonicalSMILES", "")
                })
    
    return {
        "query": query,
        "count": len(compounds),
        "compounds": compounds
    }

@app.tool("get_compound_details")
async def get_compound_details(cid: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific compound by its PubChem CID.
    
    Args:
        cid: PubChem Compound ID (CID)
        
    Returns:
        Dictionary with compound details
    """
    # Get general information
    url = f"{PUBCHEM_REST_API}/compound/cid/{cid}/record/JSON"
    response = await make_pubchem_request(url)
    
    if "error" in response:
        return response
    
    # Get additional properties
    props_url = f"{PUBCHEM_REST_API}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,ExactMass,MonoisotopicMass/JSON"
    props_response = await make_pubchem_request(props_url)
    
    # Get synonyms
    synonyms_url = f"{PUBCHEM_REST_API}/compound/cid/{cid}/synonyms/JSON"
    synonyms_response = await make_pubchem_request(synonyms_url)
    
    result = {
        "CID": cid,
        "record": response.get("PC_Compounds", [{}])[0] if "PC_Compounds" in response else {},
    }
    
    if "error" not in props_response and "PropertyTable" in props_response:
        result["properties"] = props_response["PropertyTable"]["Properties"][0] if props_response["PropertyTable"]["Properties"] else {}
    
    if "error" not in synonyms_response and "InformationList" in synonyms_response:
        synonyms = synonyms_response["InformationList"].get("Information", [{}])[0].get("Synonym", [])
        result["synonyms"] = synonyms[:10]  # Limit to 10 synonyms
    
    return result

@app.tool("get_compound_properties")
async def get_compound_properties(cid: int) -> Dict[str, Any]:
    """
    Get physical and chemical properties of a compound.
    
    Args:
        cid: PubChem Compound ID (CID)
        
    Returns:
        Dictionary with compound properties
    """
    properties = [
        "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IUPACName",
        "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount", 
        "RotatableBondCount", "ExactMass", "MonoisotopicMass", "Complexity",
        "Charge", "IsomericSMILES"
    ]
    
    property_str = ",".join(properties)
    url = f"{PUBCHEM_REST_API}/compound/cid/{cid}/property/{property_str}/JSON"
    
    response = await make_pubchem_request(url)
    
    if "error" in response:
        return response
    
    if "PropertyTable" in response and "Properties" in response["PropertyTable"]:
        return {
            "CID": cid,
            "properties": response["PropertyTable"]["Properties"][0] if response["PropertyTable"]["Properties"] else {}
        }
    
    return {"error": "No properties found", "CID": cid}

@app.tool("search_bioassay")
async def search_bioassay(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for bioassays related to a compound or target.
    
    Args:
        query: Search query (compound name, target name, etc.)
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary with bioassay search results
    """
    url = f"{PUBCHEM_REST_API}/assay/name/{query}/aids/JSON?MaxRecords={max_results}"
    response = await make_pubchem_request(url)
    
    if "error" in response:
        return response
    
    assays = []
    if "IdentifierList" in response and "AID" in response["IdentifierList"]:
        for aid in response["IdentifierList"]["AID"]:
            # Get basic info for each assay
            info_url = f"{PUBCHEM_REST_API}/assay/aid/{aid}/description/JSON"
            info = await make_pubchem_request(info_url)
            
            if "error" not in info and "PC_AssayContainer" in info:
                assay_data = info["PC_AssayContainer"][0] if info["PC_AssayContainer"] else {}
                description = assay_data.get("PC_AssayDescription", {})
                
                assays.append({
                    "AID": aid,
                    "Name": description.get("PC_AssayDescriptionName", ""),
                    "Description": description.get("PC_AssayDescriptionComment", ""),
                    "Protocol": description.get("PC_AssayDescriptionProtocol", ""),
                    "ActivityOutcome": description.get("PC_AssayDescriptionActivityOutcome", "")
                })
    
    return {
        "query": query,
        "count": len(assays),
        "assays": assays
    }

@app.tool("get_substance_details")
async def get_substance_details(sid: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific substance by its PubChem SID.
    
    Args:
        sid: PubChem Substance ID (SID)
        
    Returns:
        Dictionary with substance details
    """
    url = f"{PUBCHEM_REST_API}/substance/sid/{sid}/record/JSON"
    response = await make_pubchem_request(url)
    
    if "error" in response:
        return response
    
    # Get related compounds
    cid_url = f"{PUBCHEM_REST_API}/substance/sid/{sid}/cids/JSON"
    cid_response = await make_pubchem_request(cid_url)
    
    result = {
        "SID": sid,
        "record": response.get("PC_Substances", [{}])[0] if "PC_Substances" in response else {},
    }
    
    if "error" not in cid_response and "InformationList" in cid_response:
        info = cid_response["InformationList"].get("Information", [{}])[0]
        result["CIDs"] = info.get("CID", [])
    
    return result

if __name__ == "__main__":
    # Initialize and run the server
    app.run(transport='stdio') 