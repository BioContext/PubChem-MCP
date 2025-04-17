"""
PubChem MCP server substances module - handles substance endpoint functionality.
"""

from mcp_server import FastMCP, MCPTool
import aiohttp
import json
from ..utils import pubchem_client, BASE_URL, format_response

# Reference to the MCP server instance, set when tools are registered
mcp = None

@MCPTool(
    name="search_substance_by_name",
    description="Search for substances in PubChem by name",
    parameters=[
        {
            "name": "name",
            "description": "Name of the substance to search for",
            "type": "string",
            "required": True
        },
        {
            "name": "max_results",
            "description": "Maximum number of results to return",
            "type": "integer",
            "required": False,
            "default": 5
        }
    ]
)
async def search_substance_by_name(name: str, max_results: int = 5):
    """
    Search for substances in PubChem by name.
    
    Args:
        name: Name of the substance to search for
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary containing substance information or error message
    """
    try:
        # URL encode the name
        encoded_name = name.replace(" ", "+")
        
        # Construct URL for substance search
        url = f"{BASE_URL}/substance/name/{encoded_name}/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"No substances found matching '{name}'"
                
                if response.status != 200:
                    return f"Error searching substances: Failed to retrieve results. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "PC_Substances" not in data or not data["PC_Substances"]:
                    return f"No substances found matching '{name}'"
                
                substances = data["PC_Substances"][:max_results]
                
                # Format the results
                results = []
                for substance in substances:
                    sid = substance.get("sid", {}).get("id", {}).get("cval", "Unknown")
                    
                    # Get substance name
                    substance_name = "Unknown"
                    if "synonyms" in substance:
                        synonyms = substance.get("synonyms", [])
                        if synonyms and "synonym" in synonyms[0] and synonyms[0]["synonym"]:
                            substance_name = synonyms[0]["synonym"][0]
                    
                    # Get source
                    source = "Unknown"
                    if "source" in substance and "db" in substance["source"]:
                        source = substance["source"]["db"].get("name", "Unknown")
                    
                    # Get compound ID if available
                    cid = "Not available"
                    if "compound" in substance:
                        compound_info = substance["compound"]
                        if compound_info and "id" in compound_info and "cid" in compound_info["id"]:
                            cid = str(compound_info["id"]["cid"])
                    
                    results.append({
                        "SID": sid,
                        "Name": substance_name,
                        "Source": source,
                        "CID": cid,
                        "URL": f"https://pubchem.ncbi.nlm.nih.gov/substance/{sid}"
                    })
                
                return {
                    "Substance Details": True,
                    "Search Results": f"Found {len(results)} substances matching '{name}'",
                    "Substances": results
                }
                
    except Exception as e:
        return f"Error searching substances: {str(e)}"

@MCPTool(
    name="get_substance_details",
    description="Get detailed information about a substance by its SID",
    parameters=[
        {
            "name": "sid",
            "description": "PubChem Substance ID (SID)",
            "type": "string",
            "required": True
        }
    ]
)
async def get_substance_details(sid: str):
    """
    Get detailed information about a substance by its SID.
    
    Args:
        sid: PubChem Substance ID (SID)
        
    Returns:
        Dictionary containing substance details or error message
    """
    try:
        # Validate SID
        if not sid.isdigit():
            return f"Error: Invalid Substance ID format. SID should be a number."
        
        # Construct URL for substance details
        url = f"{BASE_URL}/substance/sid/{sid}/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Error: No substance found with SID {sid}"
                
                if response.status != 200:
                    return f"Error: Failed to retrieve substance details. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "PC_Substances" not in data or not data["PC_Substances"]:
                    return f"Error: No substance details found for SID {sid}"
                
                substance = data["PC_Substances"][0]
                
                # Get substance name
                substance_name = "Unknown"
                if "synonyms" in substance:
                    synonyms = substance.get("synonyms", [])
                    if synonyms and "synonym" in synonyms[0] and synonyms[0]["synonym"]:
                        substance_name = synonyms[0]["synonym"][0]
                
                # Get source information
                source = "Unknown"
                source_url = None
                if "source" in substance:
                    source_info = substance["source"]
                    if "db" in source_info:
                        source = source_info["db"].get("name", "Unknown")
                    if "url" in source_info:
                        source_url = source_info["url"]
                
                # Get compound ID if available
                cid = None
                if "compound" in substance:
                    compound_info = substance["compound"]
                    if compound_info and "id" in compound_info and "cid" in compound_info["id"]:
                        cid = str(compound_info["id"]["cid"])
                
                # Format the result
                result = {
                    "Substance Details": True,
                    "SID": sid,
                    "Name": substance_name,
                    "Source": source,
                    "Depositor": source,
                    "URL": f"https://pubchem.ncbi.nlm.nih.gov/substance/{sid}"
                }
                
                if cid:
                    result["CID"] = cid
                    result["Compound URL"] = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                
                if source_url:
                    result["Source URL"] = source_url
                
                # Get additional properties if available
                if "props" in substance:
                    props = substance["props"]
                    for prop in props:
                        if "urn" in prop and "label" in prop["urn"]:
                            label = prop["urn"]["label"]
                            if "value" in prop:
                                value_info = prop["value"]
                                if "sval" in value_info:
                                    result[label] = value_info["sval"]
                                elif "ival" in value_info:
                                    result[label] = str(value_info["ival"])
                                elif "fval" in value_info:
                                    result[label] = str(value_info["fval"])
                
                return result
                
    except Exception as e:
        return f"Error retrieving substance details: {str(e)}"

@MCPTool(
    name="get_substance_compounds",
    description="Get compounds associated with a substance by its SID",
    parameters=[
        {
            "name": "sid",
            "description": "PubChem Substance ID (SID)",
            "type": "string",
            "required": True
        }
    ]
)
async def get_substance_compounds(sid: str):
    """
    Get compounds associated with a substance by its SID.
    
    Args:
        sid: PubChem Substance ID (SID)
        
    Returns:
        Dictionary containing associated compounds or error message
    """
    try:
        # Validate SID
        if not sid.isdigit():
            return f"Error: Invalid Substance ID format. SID should be a number."
        
        # Construct URL for substance compounds
        url = f"{BASE_URL}/substance/sid/{sid}/cids/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Error: No substance found with SID {sid}"
                
                if response.status != 200:
                    return f"Error: Failed to retrieve substance compounds. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "InformationList" not in data or "Information" not in data["InformationList"]:
                    return f"No compounds found for substance with SID {sid}"
                
                info = data["InformationList"]["Information"][0]
                
                if "CID" not in info or not info["CID"]:
                    return f"No compounds found for substance with SID {sid}"
                
                cids = info["CID"]
                
                # Get substance name for reference
                substance_name = "Unknown"
                substance_url = f"{BASE_URL}/substance/sid/{sid}/JSON"
                async with session.get(substance_url) as substance_response:
                    if substance_response.status == 200:
                        substance_data = await substance_response.json()
                        if "PC_Substances" in substance_data and substance_data["PC_Substances"]:
                            substance = substance_data["PC_Substances"][0]
                            if "synonyms" in substance:
                                synonyms = substance.get("synonyms", [])
                                if synonyms and "synonym" in synonyms[0] and synonyms[0]["synonym"]:
                                    substance_name = synonyms[0]["synonym"][0]
                
                # Get compound details for each CID
                compounds = []
                for cid in cids:
                    compound_url = f"{BASE_URL}/compound/cid/{cid}/JSON"
                    async with session.get(compound_url) as compound_response:
                        if compound_response.status == 200:
                            compound_data = await compound_response.json()
                            if "PC_Compounds" in compound_data:
                                pc_compound = compound_data["PC_Compounds"][0]
                                
                                # Get compound name
                                name = "Unknown"
                                if "props" in pc_compound:
                                    for prop in pc_compound["props"]:
                                        if prop.get("urn", {}).get("label") == "IUPAC Name":
                                            name = prop.get("value", {}).get("sval", "Unknown")
                                            break
                                
                                compounds.append({
                                    "CID": cid,
                                    "Name": name,
                                    "URL": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                                })
                
                # Format the response
                return {
                    "Substance Compounds": f"Found {len(compounds)} compounds for substance SID {sid}",
                    "SID": sid,
                    "Substance Name": substance_name,
                    "Compounds": compounds
                }
                
    except Exception as e:
        return f"Error retrieving substance compounds: {str(e)}"

@MCPTool(
    name="search_substances_by_classification",
    description="Search for substances by classification or category",
    parameters=[
        {
            "name": "classification",
            "description": "Classification or category (e.g., 'drug', 'pesticide', 'toxin')",
            "type": "string",
            "required": True
        },
        {
            "name": "max_results",
            "description": "Maximum number of results to return",
            "type": "integer",
            "required": False,
            "default": 5
        }
    ]
)
async def search_substances_by_classification(classification: str, max_results: int = 5):
    """
    Search for substances by classification or category.
    
    Args:
        classification: Classification or category (e.g., 'drug', 'pesticide', 'toxin')
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary containing substances in the specified classification or error message
    """
    try:
        # URL encode the classification
        encoded_classification = classification.replace(" ", "+")
        
        # Construct URL for classification search
        url = f"{BASE_URL}/substance/classification/{encoded_classification}/JSON?list_return=substance"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"No substances found in classification '{classification}'"
                
                if response.status != 200:
                    return f"Error: Failed to search substances by classification. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "InformationList" not in data or "Information" not in data["InformationList"]:
                    return f"No substances found in classification '{classification}'"
                
                substances_info = data["InformationList"]["Information"][:max_results]
                
                # Format the results
                results = []
                for substance in substances_info:
                    sid = substance.get("SID", "Unknown")
                    
                    # Get substance details
                    substance_url = f"{BASE_URL}/substance/sid/{sid}/JSON"
                    async with session.get(substance_url) as substance_response:
                        if substance_response.status == 200:
                            substance_data = await substance_response.json()
                            if "PC_Substances" in substance_data and substance_data["PC_Substances"]:
                                pc_substance = substance_data["PC_Substances"][0]
                                
                                # Get substance name
                                name = "Unknown"
                                if "synonyms" in pc_substance:
                                    synonyms = pc_substance.get("synonyms", [])
                                    if synonyms and "synonym" in synonyms[0] and synonyms[0]["synonym"]:
                                        name = synonyms[0]["synonym"][0]
                                
                                # Get source
                                source = "Unknown"
                                if "source" in pc_substance and "db" in pc_substance["source"]:
                                    source = pc_substance["source"]["db"].get("name", "Unknown")
                                
                                # Get compound ID if available
                                cid = "Not available"
                                if "compound" in pc_substance:
                                    compound_info = pc_substance["compound"]
                                    if compound_info and "id" in compound_info and "cid" in compound_info["id"]:
                                        cid = str(compound_info["id"]["cid"])
                                
                                results.append({
                                    "SID": sid,
                                    "Name": name,
                                    "Source": source,
                                    "CID": cid,
                                    "Classification": classification,
                                    "URL": f"https://pubchem.ncbi.nlm.nih.gov/substance/{sid}"
                                })
                
                return {
                    "Classification Search": f"Found {len(results)} substances in classification '{classification}'",
                    "Substances": results
                }
                
    except Exception as e:
        return f"Error searching substances by classification: {str(e)}"

def register_substance_tools(mcp_instance: FastMCP):
    """Register substance-related tools with the MCP server"""
    global mcp
    mcp = mcp_instance
    # Tools are registered via the MCPTool decorator
    return {
        "search_substance_by_name": search_substance_by_name,
        "get_substance_details": get_substance_details,
        "get_substance_compounds": get_substance_compounds,
        "search_substances_by_classification": search_substances_by_classification,
    } 