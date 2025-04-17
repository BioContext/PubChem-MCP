"""
PubChem MCP server documents module - handles document and compound record endpoints.
"""

from mcp_server import FastMCP, MCPTool
import aiohttp
import json
from ..utils import pubchem_client, BASE_URL, format_response

# Reference to the MCP server instance, set when tools are registered
mcp = None

@MCPTool(
    name="get_document_details",
    description="Get details about a document in PubChem by its document ID (Reference ID)",
    parameters=[
        {
            "name": "reference_id",
            "description": "PubChem Reference ID (PMID, DOI, ISBN, etc.)",
            "type": "string",
            "required": True
        }
    ]
)
async def get_document_details(reference_id: str):
    """
    Get details about a document in PubChem by its reference ID.
    
    Args:
        reference_id: PubChem Reference ID (PMID, DOI, ISBN, etc.)
        
    Returns:
        Dictionary containing document details or error message
    """
    try:
        # Remove any URL-unsafe characters and trim whitespace
        reference_id = reference_id.strip()
        
        # Construct URL for document information
        url = f"{BASE_URL}/reference/sourceid/{reference_id}/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Error: No document found with reference ID {reference_id}"
                
                if response.status != 200:
                    return f"Error: Failed to retrieve document details. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "Record" not in data or not data["Record"]:
                    return f"Error: No document details found for reference ID {reference_id}"
                
                record = data["Record"]
                
                # Format the document information
                result = {
                    "Document Details": True,
                    "Reference ID": reference_id,
                    "Title": record.get("RecordTitle", "Not available"),
                    "Authors": ", ".join(record.get("AuthorList", {}).get("Author", [{"String": "Unknown"}])[0].get("String", "Unknown")),
                    "Source": record.get("Source", {}).get("SourceName", "Unknown"),
                    "Date": record.get("CreateDate", {}).get("Year", "Unknown"),
                    "Description": record.get("Description", "No description available"),
                }
                
                # Add DOI if available
                if "ReferenceURL" in record:
                    result["URL"] = record["ReferenceURL"]
                
                return result
                
    except Exception as e:
        return f"Error retrieving document details: {str(e)}"

@MCPTool(
    name="search_documents",
    description="Search for documents in PubChem by title, author, or keywords",
    parameters=[
        {
            "name": "query",
            "description": "Search query (title, author name, or keywords)",
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
async def search_documents(query: str, max_results: int = 5):
    """
    Search for documents in PubChem by title, author, or keywords.
    
    Args:
        query: Search query for document title, author name, or keywords
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of document results or error message
    """
    try:
        # URL encode the query
        encoded_query = query.replace(" ", "+")
        
        # Construct URL for document search
        url = f"{BASE_URL}/reference/autocomplete/{encoded_query}/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: Failed to search documents. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "Dictionary" not in data or not data["Dictionary"].get("Entry", []):
                    return f"No documents found matching '{query}'"
                
                # Process results
                results = []
                entries = data["Dictionary"]["Entry"]
                
                for entry in entries[:max_results]:
                    doc_info = {
                        "Reference ID": entry.get("ReferenceID", "Unknown"),
                        "Title": entry.get("RecordTitle", "Unknown"),
                        "Authors": entry.get("Author", "Unknown"),
                        "Source": entry.get("Source", "Unknown"),
                        "Year": entry.get("Year", "Unknown")
                    }
                    results.append(doc_info)
                
                # Format the response
                return {
                    "Search Results": f"Found {len(results)} documents matching '{query}'",
                    "Documents": results
                }
                
    except Exception as e:
        return f"Error searching documents: {str(e)}"

@MCPTool(
    name="get_document_compounds",
    description="Get compounds mentioned in a document by its reference ID",
    parameters=[
        {
            "name": "reference_id",
            "description": "PubChem Reference ID (PMID, DOI, ISBN, etc.)",
            "type": "string",
            "required": True
        },
        {
            "name": "max_results",
            "description": "Maximum number of compounds to return",
            "type": "integer",
            "required": False,
            "default": 10
        }
    ]
)
async def get_document_compounds(reference_id: str, max_results: int = 10):
    """
    Get compounds mentioned in a document by its reference ID.
    
    Args:
        reference_id: PubChem Reference ID (PMID, DOI, ISBN, etc.)
        max_results: Maximum number of compounds to return
        
    Returns:
        List of compounds mentioned in the document or error message
    """
    try:
        # Remove any URL-unsafe characters and trim whitespace
        reference_id = reference_id.strip()
        
        # Construct URL for document compounds
        url = f"{BASE_URL}/reference/sourceid/{reference_id}/cids/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Error: No document found with reference ID {reference_id}"
                
                if response.status != 200:
                    return f"Error: Failed to retrieve document compounds. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "InformationList" not in data or "Information" not in data["InformationList"]:
                    return f"No compounds found for document with reference ID {reference_id}"
                
                info = data["InformationList"]["Information"][0]
                
                if "CID" not in info or not info["CID"]:
                    return f"No compounds found for document with reference ID {reference_id}"
                
                cids = info["CID"][:max_results]
                
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
                    "Document Compounds": f"Found {len(compounds)} compounds in document {reference_id}",
                    "Reference ID": reference_id,
                    "Compounds": compounds
                }
                
    except Exception as e:
        return f"Error retrieving document compounds: {str(e)}"

@MCPTool(
    name="get_compound_references",
    description="Get references/documents that mention a specific compound",
    parameters=[
        {
            "name": "cid",
            "description": "PubChem Compound ID (CID)",
            "type": "string",
            "required": True
        },
        {
            "name": "max_results",
            "description": "Maximum number of references to return",
            "type": "integer",
            "required": False,
            "default": 5
        }
    ]
)
async def get_compound_references(cid: str, max_results: int = 5):
    """
    Get references/documents that mention a specific compound.
    
    Args:
        cid: PubChem Compound ID (CID)
        max_results: Maximum number of references to return
        
    Returns:
        List of references mentioning the compound or error message
    """
    try:
        # Validate CID
        if not cid.isdigit():
            return f"Error: Invalid Compound ID format. CID should be a number."
        
        # Construct URL for compound references
        url = f"{BASE_URL}/compound/cid/{cid}/literature/JSON"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Error: No compound found with CID {cid}"
                
                if response.status != 200:
                    return f"Error: Failed to retrieve compound references. Status code: {response.status}"
                
                data = await response.json()
                
                if not data or "InformationList" not in data or "Information" not in data["InformationList"]:
                    return f"No references found for compound with CID {cid}"
                
                info = data["InformationList"]["Information"][0]
                
                if "ReferenceID" not in info or not info["ReferenceID"]:
                    return f"No references found for compound with CID {cid}"
                
                reference_ids = info["ReferenceID"][:max_results]
                
                # Get reference details for each reference ID
                references = []
                for ref_id in reference_ids:
                    ref_url = f"{BASE_URL}/reference/pubmed/{ref_id}/JSON"
                    async with session.get(ref_url) as ref_response:
                        if ref_response.status == 200:
                            ref_data = await ref_response.json()
                            if "Record" in ref_data:
                                record = ref_data["Record"]
                                
                                # Get author information
                                authors = "Unknown"
                                if "AuthorList" in record and "Author" in record["AuthorList"]:
                                    author_list = record["AuthorList"]["Author"]
                                    if author_list and "String" in author_list[0]:
                                        authors = author_list[0]["String"]
                                
                                references.append({
                                    "Reference ID": ref_id,
                                    "Title": record.get("RecordTitle", "Unknown"),
                                    "Authors": authors,
                                    "Source": record.get("Source", {}).get("SourceName", "Unknown"),
                                    "Year": record.get("CreateDate", {}).get("Year", "Unknown"),
                                    "URL": f"https://pubmed.ncbi.nlm.nih.gov/{ref_id}/"
                                })
                
                # Format the response
                return {
                    "Compound References": f"Found {len(references)} references for compound CID {cid}",
                    "CID": cid,
                    "References": references
                }
                
    except Exception as e:
        return f"Error retrieving compound references: {str(e)}"

def register_document_tools(mcp_instance: FastMCP):
    """Register document-related tools with the MCP server"""
    global mcp
    mcp = mcp_instance
    # Tools are registered via the MCPTool decorator
    return {
        "get_document_details": get_document_details,
        "search_documents": search_documents,
        "get_document_compounds": get_document_compounds,
        "get_compound_references": get_compound_references,
    } 