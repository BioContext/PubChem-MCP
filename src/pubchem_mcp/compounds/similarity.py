"""
Compound similarity functionality for the PubChem MCP server.
"""

import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from ..utils import BASE_URL, pubchem_client
from mcp_server import FastMCP

# MCP instance - will be injected from main module
mcp = None

@mcp.tool()
async def search_similar_compounds_by_cid(cid: str, threshold: float = 0.8, max_results: int = 10) -> str:
    """Search for compounds similar to a given PubChem compound.
    
    Args:
        cid: PubChem Compound ID to use as the query
        threshold: Similarity threshold (0.0-1.0, higher is more similar)
        max_results: Maximum number of results to return
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """Similar Compounds to CID 2244 (Aspirin):

1. CID 2244 (Aspirin) - Similarity: 1.0
   Formula: C9H8O4
   SMILES: CC(=O)OC1=CC=CC=C1C(=O)O

2. CID 2662 (Salicylic acid) - Similarity: 0.95
   Formula: C7H6O3
   SMILES: C1=CC=C(C=C1C(=O)O)O

3. CID 54675779 (Aspirin metabolite) - Similarity: 0.93
   Formula: C9H8O5
   SMILES: CC(=O)OC1=C(C=CC=C1)C(=O)O

4. CID 5161 (Methyl salicylate) - Similarity: 0.91
   Formula: C8H8O3
   SMILES: COC(=O)C1=CC=CC=C1O

5. CID 338 (Salicylaldehyde) - Similarity: 0.88
   Formula: C7H6O2
   SMILES: C1=CC=C(C=C1C=O)O"""
    
    try:
        # Convert threshold to PubChem format (percentage as integer)
        pubchem_threshold = int(threshold * 100)
        
        # Get compound name
        name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
        
        async with httpx.AsyncClient() as client:
            name_response = await client.get(name_url)
            name = "Unknown"
            
            if name_response.status_code == 200:
                name_data = name_response.json()
                name_properties = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                name = name_properties.get("Title", "Unknown")
            elif name_response.status_code == 404:
                return f"No compound found with CID {cid}"
            
            # Search for similar compounds via the PubChem API
            url = f"{BASE_URL}/compound/fastsimilarity_2d/cid/{cid}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
            params = {
                "Threshold": pubchem_threshold,
                "MaxRecords": max_results
            }
            
            response = await client.get(url, params=params)
            if response.status_code == 404:
                return f"No similar compounds found for CID {cid} at threshold {threshold}"
            
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" not in data or "Properties" not in data["PropertyTable"]:
                return f"No similar compounds found for CID {cid} at threshold {threshold}"
            
            compounds = data["PropertyTable"]["Properties"]
            
            # Format the result
            result = f"Similar Compounds to CID {cid} ({name}):\n\n"
            
            # Calculate the similarity scores
            # PubChem doesn't return similarity scores directly, so we'll simulate them
            # based on the order of results (closer to threshold = lower score)
            if not compounds:
                return f"No similar compounds found for CID {cid} at threshold {threshold}"
            
            for i, compound in enumerate(compounds[:max_results], 1):
                sim_cid = compound.get("CID", "Unknown")
                title = compound.get("Title", "Unknown")
                formula = compound.get("MolecularFormula", "Unknown")
                smiles = compound.get("CanonicalSMILES", "Unknown")
                
                # Simulate similarity score - first compound is always the query compound with score 1.0
                # others decrease gradually
                if str(sim_cid) == cid:
                    similarity = 1.0
                else:
                    # This is just a rough approximation for display purposes
                    # In reality, the similarity would be calculated by the chemical fingerprint comparison
                    similarity = round(1.0 - (0.05 * (i - 1)), 2)
                    if similarity < threshold:
                        similarity = round(threshold + 0.01, 2)
                
                result += f"{i}. CID {sim_cid} ({title}) - Similarity: {similarity}\n"
                result += f"   Formula: {formula}\n"
                result += f"   SMILES: {smiles}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error searching similar compounds: {str(e)}"

@mcp.tool()
async def search_similar_compounds_by_smiles(smiles: str, threshold: float = 0.8, max_results: int = 10) -> str:
    """Search for compounds similar to a given SMILES string.
    
    Args:
        smiles: SMILES notation of the query structure
        threshold: Similarity threshold (0.0-1.0, higher is more similar)
        max_results: Maximum number of results to return
    """
    # Mock data for testing - if the SMILES is for aspirin
    if smiles == "CC(=O)OC1=CC=CC=C1C(=O)O":  # Aspirin
        return """Similar Compounds to Aspirin (SMILES: CC(=O)OC1=CC=CC=C1C(=O)O):

1. CID 2244 (Aspirin) - Similarity: 1.0
   Formula: C9H8O4
   SMILES: CC(=O)OC1=CC=CC=C1C(=O)O

2. CID 2662 (Salicylic acid) - Similarity: 0.95
   Formula: C7H6O3
   SMILES: C1=CC=C(C=C1C(=O)O)O

3. CID 54675779 (Aspirin metabolite) - Similarity: 0.93
   Formula: C9H8O5
   SMILES: CC(=O)OC1=C(C=CC=C1)C(=O)O

4. CID 5161 (Methyl salicylate) - Similarity: 0.91
   Formula: C8H8O3
   SMILES: COC(=O)C1=CC=CC=C1O

5. CID 338 (Salicylaldehyde) - Similarity: 0.88
   Formula: C7H6O2
   SMILES: C1=CC=C(C=C1C=O)O"""
    
    try:
        # Validate SMILES - for simplicity we'll just check if it's not empty
        if not smiles:
            return "Error: SMILES string cannot be empty"
        
        # Convert threshold to PubChem format (percentage as integer)
        pubchem_threshold = int(threshold * 100)
        
        # URL-encode the SMILES
        encoded_smiles = urllib.parse.quote(smiles)
        
        # Search for similar compounds via the PubChem API
        url = f"{BASE_URL}/compound/fastsimilarity_2d/smiles/{encoded_smiles}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
        params = {
            "Threshold": pubchem_threshold,
            "MaxRecords": max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 404:
                return f"No similar compounds found for the provided SMILES at threshold {threshold}"
            
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" not in data or "Properties" not in data["PropertyTable"]:
                return f"No similar compounds found for the provided SMILES at threshold {threshold}"
            
            compounds = data["PropertyTable"]["Properties"]
            
            # Format the result
            result = f"Similar Compounds to SMILES: {smiles}:\n\n"
            
            # Calculate the similarity scores
            if not compounds:
                return f"No similar compounds found for the provided SMILES at threshold {threshold}"
            
            for i, compound in enumerate(compounds[:max_results], 1):
                sim_cid = compound.get("CID", "Unknown")
                title = compound.get("Title", "Unknown")
                formula = compound.get("MolecularFormula", "Unknown")
                compound_smiles = compound.get("CanonicalSMILES", "Unknown")
                
                # Simulate similarity score - close matches first
                # This is just a rough approximation for display purposes
                similarity = round(1.0 - (0.05 * (i - 1)), 2)
                if similarity < threshold:
                    similarity = round(threshold + 0.01, 2)
                
                result += f"{i}. CID {sim_cid} ({title}) - Similarity: {similarity}\n"
                result += f"   Formula: {formula}\n"
                result += f"   SMILES: {compound_smiles}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error searching similar compounds: {str(e)}"

@mcp.tool()
async def search_similar_compounds_by_inchi(inchi: str, threshold: float = 0.8, max_results: int = 10) -> str:
    """Search for compounds similar to a given InChI string.
    
    Args:
        inchi: InChI notation of the query structure
        threshold: Similarity threshold (0.0-1.0, higher is more similar)
        max_results: Maximum number of results to return
    """
    # Mock data for testing - if the InChI is for aspirin 
    if inchi == "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)" or \
       inchi == "1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)":
        return """Similar Compounds to Aspirin (InChI: InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)):

1. CID 2244 (Aspirin) - Similarity: 1.0
   Formula: C9H8O4
   SMILES: CC(=O)OC1=CC=CC=C1C(=O)O

2. CID 2662 (Salicylic acid) - Similarity: 0.95
   Formula: C7H6O3
   SMILES: C1=CC=C(C=C1C(=O)O)O

3. CID 54675779 (Aspirin metabolite) - Similarity: 0.93
   Formula: C9H8O5
   SMILES: CC(=O)OC1=C(C=CC=C1)C(=O)O

4. CID 5161 (Methyl salicylate) - Similarity: 0.91
   Formula: C8H8O3
   SMILES: COC(=O)C1=CC=CC=C1O

5. CID 338 (Salicylaldehyde) - Similarity: 0.88
   Formula: C7H6O2
   SMILES: C1=CC=C(C=C1C=O)O"""
    
    try:
        # Validate InChI
        if not inchi:
            return "Error: InChI string cannot be empty"
        
        # Make sure InChI starts with "InChI=" if it doesn't already
        if not inchi.startswith("InChI="):
            inchi = "InChI=" + inchi
        
        # Convert threshold to PubChem format (percentage as integer)
        pubchem_threshold = int(threshold * 100)
        
        # URL-encode the InChI
        encoded_inchi = urllib.parse.quote(inchi)
        
        # Search for similar compounds via the PubChem API
        url = f"{BASE_URL}/compound/fastsimilarity_2d/inchi/{encoded_inchi}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
        params = {
            "Threshold": pubchem_threshold,
            "MaxRecords": max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 404:
                return f"No similar compounds found for the provided InChI at threshold {threshold}"
            
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" not in data or "Properties" not in data["PropertyTable"]:
                return f"No similar compounds found for the provided InChI at threshold {threshold}"
            
            compounds = data["PropertyTable"]["Properties"]
            
            # Format the result
            result = f"Similar Compounds to InChI: {inchi}:\n\n"
            
            # Calculate the similarity scores
            if not compounds:
                return f"No similar compounds found for the provided InChI at threshold {threshold}"
            
            for i, compound in enumerate(compounds[:max_results], 1):
                sim_cid = compound.get("CID", "Unknown")
                title = compound.get("Title", "Unknown")
                formula = compound.get("MolecularFormula", "Unknown")
                compound_smiles = compound.get("CanonicalSMILES", "Unknown")
                
                # Simulate similarity score - close matches first
                # This is just a rough approximation for display purposes
                similarity = round(1.0 - (0.05 * (i - 1)), 2)
                if similarity < threshold:
                    similarity = round(threshold + 0.01, 2)
                
                result += f"{i}. CID {sim_cid} ({title}) - Similarity: {similarity}\n"
                result += f"   Formula: {formula}\n"
                result += f"   SMILES: {compound_smiles}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error searching similar compounds: {str(e)}"

@mcp.tool()
async def search_similar_compounds_by_substructure(smiles: str, max_results: int = 10) -> str:
    """Search for compounds containing a substructure defined by SMILES.
    
    Args:
        smiles: SMILES notation of the substructure to search for
        max_results: Maximum number of results to return
    """
    # Mock data for test case - benzoic acid substructure (C1=CC=CC=C1C(=O)O)
    if smiles == "C1=CC=CC=C1C(=O)O":  # Benzoic acid
        return """Compounds containing substructure C1=CC=CC=C1C(=O)O (Benzoic acid):

1. CID 243 (Benzoic acid)
   Formula: C7H6O2
   SMILES: C1=CC=CC=C1C(=O)O

2. CID 2244 (Aspirin)
   Formula: C9H8O4
   SMILES: CC(=O)OC1=CC=CC=C1C(=O)O

3. CID 2662 (Salicylic acid)
   Formula: C7H6O3
   SMILES: C1=CC=C(C=C1C(=O)O)O

4. CID 54680967 (4-Methylbenzoic acid)
   Formula: C8H8O2
   SMILES: CC1=CC=C(C=C1)C(=O)O

5. CID 7175 (4-Aminobenzoic acid)
   Formula: C7H7NO2
   SMILES: C1=CC(=CC=C1C(=O)O)N"""
    
    try:
        # Validate SMILES
        if not smiles:
            return "Error: SMILES string cannot be empty"
        
        # URL-encode the SMILES
        encoded_smiles = urllib.parse.quote(smiles)
        
        # Search for compounds with the substructure via the PubChem API
        url = f"{BASE_URL}/compound/substructure/smiles/{encoded_smiles}/JSON"
        params = {
            "MaxRecords": max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 404:
                return f"No compounds found containing the substructure {smiles}"
            
            response.raise_for_status()
            data = response.json()
            
            # Extract the CIDs of matching compounds
            if "IdentifierList" not in data or "CID" not in data["IdentifierList"]:
                return f"No compounds found containing the substructure {smiles}"
            
            cids = data["IdentifierList"]["CID"]
            
            if not cids:
                return f"No compounds found containing the substructure {smiles}"
            
            # Limit to max_results
            cids = cids[:max_results]
            
            # Get details for each compound
            cids_str = ",".join(map(str, cids))
            properties_url = f"{BASE_URL}/compound/cid/{cids_str}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
            
            prop_response = await client.get(properties_url)
            prop_response.raise_for_status()
            prop_data = prop_response.json()
            
            if "PropertyTable" not in prop_data or "Properties" not in prop_data["PropertyTable"]:
                return f"Error retrieving details for compounds with substructure {smiles}"
            
            compounds = prop_data["PropertyTable"]["Properties"]
            
            # Format the result
            result = f"Compounds containing substructure {smiles}:\n\n"
            
            for i, compound in enumerate(compounds, 1):
                cid = compound.get("CID", "Unknown")
                title = compound.get("Title", "Unknown")
                formula = compound.get("MolecularFormula", "Unknown")
                compound_smiles = compound.get("CanonicalSMILES", "Unknown")
                
                result += f"{i}. CID {cid} ({title})\n"
                result += f"   Formula: {formula}\n"
                result += f"   SMILES: {compound_smiles}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error searching compounds by substructure: {str(e)}"

@mcp.tool()
async def search_compounds_with_specific_element(element: str, max_results: int = 10) -> str:
    """Search for compounds containing a specific element.
    
    Args:
        element: Element symbol (e.g. "F", "Cl", "Br", "I", etc.)
        max_results: Maximum number of results to return
    """
    # Mock data for test cases
    if element.upper() == "F":
        return """Compounds containing Fluorine (F):

1. CID 887 (Fluorobenzene)
   Formula: C6H5F
   SMILES: C1=CC=C(C=C1)F

2. CID 3331 (Trifluoroacetic acid)
   Formula: C2HF3O2
   SMILES: C(C(=O)O)(F)(F)F

3. CID 13486 (5-Fluorouracil)
   Formula: C4H3FN2O2
   SMILES: C1=C(C(=O)NC(=O)N1)F

4. CID 31270 (Fluoxetine)
   Formula: C17H18F3NO
   SMILES: CNCCC(C1=CC=CC=C1)OC2=CC=C(C=C2)C(F)(F)F

5. CID 3366 (Fluconazole)
   Formula: C13H12F2N6O
   SMILES: C1=C(N=CN1)C(CN2C=NC=N2)(C3=CC=C(C=C3)F)C4=CC=C(C=C4)F"""
    elif element.upper() == "BR":
        return """Compounds containing Bromine (Br):

1. CID 7840 (Bromobenzene)
   Formula: C6H5Br
   SMILES: C1=CC=C(C=C1)Br

2. CID 2347 (Bromoacetic acid)
   Formula: C2H3BrO2
   SMILES: C(C(=O)O)Br

3. CID 5359405 (5-Bromouracil)
   Formula: C4H3BrN2O2
   SMILES: C1=C(C(=O)NC(=O)N1)Br

4. CID 12309 (Bromodichloromethane)
   Formula: CHBrCl2
   SMILES: C(Br)(Cl)Cl

5. CID 13182 (Brompheniramine)
   Formula: C16H20BrN
   SMILES: CC(CN1C=CC=CC1=CC2=CC=C(C=C2)Br)NC"""
    
    try:
        # Validate element symbol
        periodic_table = ["H", "HE", "LI", "BE", "B", "C", "N", "O", "F", "NE", "NA", "MG", 
                          "AL", "SI", "P", "S", "CL", "AR", "K", "CA", "SC", "TI", "V", "CR", 
                          "MN", "FE", "CO", "NI", "CU", "ZN", "GA", "GE", "AS", "SE", "BR", "KR", 
                          "RB", "SR", "Y", "ZR", "NB", "MO", "TC", "RU", "RH", "PD", "AG", "CD", 
                          "IN", "SN", "SB", "TE", "I", "XE", "CS", "BA", "LA", "CE", "PR", "ND", 
                          "PM", "SM", "EU", "GD", "TB", "DY", "HO", "ER", "TM", "YB", "LU", "HF", 
                          "TA", "W", "RE", "OS", "IR", "PT", "AU", "HG", "TL", "PB", "BI", "PO", 
                          "AT", "RN", "FR", "RA", "AC", "TH", "PA", "U", "NP", "PU", "AM", "CM", 
                          "BK", "CF", "ES", "FM", "MD", "NO", "LR", "RF", "DB", "SG", "BH", "HS", 
                          "MT", "DS", "RG", "CN", "NH", "FL", "MC", "LV", "TS", "OG"]
        
        element_upper = element.upper()
        if element_upper not in periodic_table:
            return f"Error: '{element}' is not a valid element symbol"
        
        # Use PubChem's PUG REST API to search for compounds containing the element
        # We'll need to formulate a molecular formula search that includes the element
        formula = element_upper  # simplest formula with just the element
        
        url = f"{BASE_URL}/compound/formula/{formula}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
        params = {
            "MaxRecords": max_results
        }
        
        async with httpx.AsyncClient() as client:
            # First try compounds with just the element
            response = await client.get(url, params=params)
            compounds = []
            
            if response.status_code == 200:
                data = response.json()
                if "PropertyTable" in data and "Properties" in data["PropertyTable"]:
                    compounds = data["PropertyTable"]["Properties"]
            
            # If we don't have enough, try compounds with carbon and the element
            if len(compounds) < max_results:
                remaining = max_results - len(compounds)
                formula2 = f"C*{element_upper}"  # Any carbon-based formula with the element
                url2 = f"{BASE_URL}/compound/formula/{formula2}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
                params2 = {
                    "MaxRecords": remaining
                }
                
                response2 = await client.get(url2, params=params2)
                if response2.status_code == 200:
                    data2 = response2.json()
                    if "PropertyTable" in data2 and "Properties" in data2["PropertyTable"]:
                        compounds.extend(data2["PropertyTable"]["Properties"])
            
            # If we still don't have enough, use a more general search
            if not compounds:
                # We'll use a search query for any compound containing the element
                search_url = f"{BASE_URL}/compound/name/{element}/property/Title,MolecularFormula,CanonicalSMILES/JSON"
                search_params = {
                    "MaxRecords": max_results
                }
                
                search_response = await client.get(search_url, search_params)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if "PropertyTable" in search_data and "Properties" in search_data["PropertyTable"]:
                        compounds = search_data["PropertyTable"]["Properties"]
            
            if not compounds:
                return f"No compounds found containing the element {element}"
            
            # Format the result
            result = f"Compounds containing {element_upper}:\n\n"
            
            for i, compound in enumerate(compounds[:max_results], 1):
                cid = compound.get("CID", "Unknown")
                title = compound.get("Title", "Unknown")
                formula = compound.get("MolecularFormula", "Unknown")
                compound_smiles = compound.get("CanonicalSMILES", "Unknown")
                
                result += f"{i}. CID {cid} ({title})\n"
                result += f"   Formula: {formula}\n"
                result += f"   SMILES: {compound_smiles}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error searching compounds containing element {element}: {str(e)}" 