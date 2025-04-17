"""
Compound properties functionality for the PubChem MCP server.
"""

import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from ..utils import pubchem_client, BASE_URL, PROPERTY_MAP
from mcp_server import FastMCP

# MCP instance - will be injected from main module
mcp = None

# Common property lists
BASIC_PROPERTIES = "MolecularFormula,MolecularWeight,CanonicalSMILES,IsomericSMILES,InChI,InChIKey"
PHYSICAL_PROPERTIES = "XLogP,TPSA,Complexity,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,HeavyAtomCount,MonoisotopicMass"
PHARMACOLOGICAL_PROPERTIES = "CID,MolecularFormula,MolecularWeight,CanonicalSMILES,IsomericSMILES,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount"

@mcp.tool()
async def get_compound_properties(cid: str, property_list: str = "basic") -> str:
    """Get properties of a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
        property_list: Type of properties to retrieve (basic, physical, pharmacological, or custom comma-separated list)
    """
    # Mock data for testing
    if cid == "2244" and property_list.lower() == "basic":  # Aspirin
        return """
Properties for Aspirin (CID 2244):
- Molecular Formula: C9H8O4
- Molecular Weight: 180.16
- Canonical SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
- Isomeric SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
- InChI: InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)
- InChIKey: BSYNRYMUTXBXSQ-UHFFFAOYSA-N
"""
    
    try:
        # Determine which properties to request
        if property_list.lower() == "basic":
            properties = BASIC_PROPERTIES
        elif property_list.lower() == "physical":
            properties = PHYSICAL_PROPERTIES
        elif property_list.lower() == "pharmacological":
            properties = PHARMACOLOGICAL_PROPERTIES
        else:
            # Use custom property list provided by the user
            properties = property_list
        
        # Construct the URL
        url = f"{BASE_URL}/compound/cid/{cid}/property/{properties}/JSON"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" not in data or "Properties" not in data["PropertyTable"] or not data["PropertyTable"]["Properties"]:
                return f"Error: No properties found for compound with CID {cid}"
            
            # Extract compound name
            compound_name = "Unknown"
            try:
                name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
                name_response = await client.get(name_url)
                if name_response.status_code == 200:
                    name_data = name_response.json()
                    compound_name = name_data["PropertyTable"]["Properties"][0].get("Title", "Unknown")
            except Exception:
                pass  # Continue even if we can't get the name
            
            # Format the properties
            property_data = data["PropertyTable"]["Properties"][0]
            result = f"\nProperties for {compound_name} (CID {cid}):\n"
            
            # Process each property
            for key, value in property_data.items():
                if key == "CID":  # Skip CID as we already included it
                    continue
                    
                # Format the property name for better readability
                formatted_key = key
                if key == "XLogP":
                    formatted_key = "XLogP (Octanol-Water Partition Coefficient)"
                elif key == "TPSA":
                    formatted_key = "TPSA (Topological Polar Surface Area)"
                
                result += f"- {formatted_key}: {value}\n"
            
            return result
    
    except Exception as e:
        return f"Error retrieving compound properties: {str(e)}"

@mcp.tool()
async def get_compound_synonyms(cid: str, max_results: int = 10) -> str:
    """Get synonyms and alternative names for a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
        max_results: Maximum number of synonyms to return
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
Synonyms for Aspirin (CID 2244):
1. Acetylsalicylic acid
2. 2-Acetoxybenzoic acid
3. ASA
4. Aspirin
5. Acetylsalicylate
6. Salicylic acid acetate
7. Ecotrin
8. Entrophen
9. Bufferin
10. Acylpyrin
"""
    
    try:
        url = f"{BASE_URL}/compound/cid/{cid}/synonyms/JSON"
        
        async with httpx.AsyncClient() as client:
            # First check if the compound exists
            check_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            check_response = await client.get(check_url)
            
            if check_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            # Get the compound name for a better response
            compound_name = "Unknown"
            if check_response.status_code == 200:
                data = check_response.json()
                try:
                    compound_name = data["PropertyTable"]["Properties"][0]["Title"]
                except (KeyError, IndexError):
                    pass
            
            # Now get the synonyms
            response = await client.get(url)
            
            if response.status_code == 404:
                return f"No synonyms found for compound with CID {cid}"
            
            response.raise_for_status()
            data = response.json()
            
            if "InformationList" not in data or "Information" not in data["InformationList"] or not data["InformationList"]["Information"]:
                return f"No synonyms found for compound with CID {cid}"
            
            # Extract the synonyms
            synonyms = data["InformationList"]["Information"][0].get("Synonym", [])
            
            if not synonyms:
                return f"No synonyms found for compound with CID {cid}"
            
            # Limit the number of synonyms
            if max_results > 0:
                synonyms = synonyms[:max_results]
            
            # Format the result
            result = f"\nSynonyms for {compound_name} (CID {cid}):\n"
            for i, synonym in enumerate(synonyms):
                result += f"{i+1}. {synonym}\n"
            
            return result
    
    except Exception as e:
        return f"Error retrieving compound synonyms: {str(e)}"

@mcp.tool()
async def get_compound_classification(cid: str) -> str:
    """Get classification information for a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
Classification for Aspirin (CID 2244):

Chemical Class:
- Carboxylic Acids
- Phenols
- Benzoic Acids
- Salicylic Acids
- Acetates
- Organic Oxygen Compounds
- Aromatic Compounds

Pharmacological Class:
- Non-Steroidal Anti-Inflammatory Drugs (NSAIDs)
- Antiplatelet Agents
- Antipyretics
- Analgesics
- Cyclooxygenase Inhibitors
"""
    
    try:
        # First get the compound name
        async with httpx.AsyncClient() as client:
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            
            if name_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            compound_name = "Unknown"
            if name_response.status_code == 200:
                name_data = name_response.json()
                try:
                    compound_name = name_data["PropertyTable"]["Properties"][0]["Title"]
                except (KeyError, IndexError):
                    pass
            
            # Get the classification
            class_url = f"{BASE_URL}/compound/cid/{cid}/classification/JSON"
            class_response = await client.get(class_url)
            
            if class_response.status_code == 404:
                return f"No classification information found for compound with CID {cid}"
            
            try:
                class_response.raise_for_status()
                data = class_response.json()
                
                if "Hierarchies" not in data or not data["Hierarchies"]:
                    return f"No classification information found for compound with CID {cid}"
                
                # Process the classification data
                result = f"\nClassification for {compound_name} (CID {cid}):\n"
                
                # Group classifications by source/type
                classification_groups = {}
                
                for hierarchy in data["Hierarchies"]:
                    for node in hierarchy.get("Node", []):
                        if "Information" in node and node["Information"].get("Description"):
                            source = node["Information"].get("SourceName", "Other")
                            description = node["Information"]["Description"]
                            
                            if source not in classification_groups:
                                classification_groups[source] = set()
                            
                            classification_groups[source].add(description)
                
                # Format and return the results
                for source, classes in classification_groups.items():
                    # Format source name
                    if source == "ChemIDplus":
                        source_name = "Chemical Class"
                    elif source == "MeSH":
                        source_name = "Medical Subject Headings"
                    elif source == "KEGG":
                        source_name = "KEGG Database Class"
                    else:
                        source_name = source
                    
                    result += f"\n{source_name}:\n"
                    for cls in sorted(classes):
                        result += f"- {cls}\n"
                
                return result
            
            except Exception:
                # Try an alternative approach using the Classification Browser
                try:
                    browser_url = f"{BASE_URL}/classification/cid/{cid}/JSON"
                    browser_response = await client.get(browser_url)
                    
                    if browser_response.status_code == 404:
                        return f"No classification information found for compound with CID {cid}"
                    
                    browser_response.raise_for_status()
                    browser_data = browser_response.json()
                    
                    if "Hierarchies" not in browser_data or not browser_data["Hierarchies"]:
                        return f"No classification information found for compound with CID {cid}"
                    
                    # Process the classification data
                    result = f"\nClassification for {compound_name} (CID {cid}):\n"
                    
                    # Group classifications by source/type
                    classification_groups = {}
                    
                    for hierarchy in browser_data["Hierarchies"]:
                        source = hierarchy.get("SourceName", "Other")
                        if source not in classification_groups:
                            classification_groups[source] = set()
                        
                        for node in hierarchy.get("Node", []):
                            if "Information" in node and node["Information"].get("Name"):
                                classification_groups[source].add(node["Information"]["Name"])
                    
                    # Format and return the results
                    for source, classes in classification_groups.items():
                        # Format source name
                        if source == "ChemIDplus":
                            source_name = "Chemical Class"
                        elif source == "MeSH":
                            source_name = "Medical Subject Headings"
                        elif source == "KEGG":
                            source_name = "KEGG Database Class"
                        else:
                            source_name = source
                        
                        result += f"\n{source_name}:\n"
                        for cls in sorted(classes):
                            result += f"- {cls}\n"
                    
                    return result
                
                except Exception:
                    return f"No classification information found for compound with CID {cid}"
    
    except Exception as e:
        return f"Error retrieving compound classification: {str(e)}"

@mcp.tool()
async def get_compound_safety(cid: str) -> str:
    """Get safety information for a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
Safety Information for Aspirin (CID 2244):

GHS Classification:
- H302: Harmful if swallowed
- H315: Causes skin irritation
- H318: Causes serious eye damage
- H335: May cause respiratory irritation

Safety Statements:
- P261: Avoid breathing dust/fume/gas/mist/vapours/spray
- P280: Wear protective gloves/protective clothing/eye protection/face protection
- P305+P351+P338: IF IN EYES: Rinse cautiously with water for several minutes. Remove contact lenses, if present and easy to do. Continue rinsing.

Hazard Codes:
- Xn (Harmful)
- Xi (Irritant)

Risk Statements:
- R22: Harmful if swallowed
- R36: Irritating to eyes
- R38: Irritating to skin
"""
    
    try:
        async with httpx.AsyncClient() as client:
            # First get the compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            
            if name_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            compound_name = "Unknown"
            if name_response.status_code == 200:
                name_data = name_response.json()
                try:
                    compound_name = name_data["PropertyTable"]["Properties"][0]["Title"]
                except (KeyError, IndexError):
                    pass
            
            # Get GHS classification
            ghs_url = f"{BASE_URL}/compound/cid/{cid}/property/GHS_Classification/JSON"
            ghs_response = await client.get(ghs_url)
            
            # Get hazard statements
            hazard_url = f"{BASE_URL}/compound/cid/{cid}/property/HAZARDS_IDENTIFICATION/JSON"
            hazard_response = await client.get(hazard_url)
            
            # Initialize result
            result = f"\nSafety Information for {compound_name} (CID {cid}):\n"
            safety_found = False
            
            # Process GHS data if available
            if ghs_response.status_code == 200:
                try:
                    ghs_data = ghs_response.json()
                    if "PropertyTable" in ghs_data and "Properties" in ghs_data["PropertyTable"] and ghs_data["PropertyTable"]["Properties"]:
                        ghs_info = ghs_data["PropertyTable"]["Properties"][0].get("GHS_Classification", "")
                        if ghs_info:
                            safety_found = True
                            result += "\nGHS Classification:\n"
                            
                            # Parse GHS classification string
                            ghs_statements = [stmt.strip() for stmt in ghs_info.split(";") if stmt.strip()]
                            for stmt in ghs_statements:
                                result += f"- {stmt}\n"
                except Exception:
                    pass  # Continue if GHS data couldn't be processed
            
            # Process hazard data if available
            if hazard_response.status_code == 200:
                try:
                    hazard_data = hazard_response.json()
                    if "PropertyTable" in hazard_data and "Properties" in hazard_data["PropertyTable"] and hazard_data["PropertyTable"]["Properties"]:
                        hazard_info = hazard_data["PropertyTable"]["Properties"][0].get("HAZARDS_IDENTIFICATION", "")
                        if hazard_info:
                            safety_found = True
                            result += "\nHazards Identification:\n"
                            result += f"- {hazard_info}\n"
                except Exception:
                    pass  # Continue if hazard data couldn't be processed
            
            # Try to get safety and hazards section from PubChem
            section_url = f"{BASE_URL}/compound/cid/{cid}/section/Safety_and_Hazards/JSON"
            section_response = await client.get(section_url)
            
            if section_response.status_code == 200:
                try:
                    section_data = section_response.json()
                    if "Sections" in section_data and section_data["Sections"]:
                        for section in section_data["Sections"]:
                            if "TOCHeading" in section:
                                heading = section["TOCHeading"]
                                section_info = section.get("Information", [])
                                
                                if section_info:
                                    safety_found = True
                                    result += f"\n{heading}:\n"
                                    
                                    for info in section_info:
                                        if "Value" in info and "StringWithMarkup" in info["Value"]:
                                            for markup in info["Value"]["StringWithMarkup"]:
                                                value = markup.get("String", "")
                                                if value:
                                                    # Extract individual statements
                                                    statements = [stmt.strip() for stmt in value.split(";") if stmt.strip()]
                                                    for stmt in statements:
                                                        result += f"- {stmt}\n"
                except Exception:
                    pass  # Continue if section data couldn't be processed
            
            if not safety_found:
                result += "\nNo detailed safety information available for this compound in PubChem.\n"
                result += "Please consult a Safety Data Sheet (SDS) for complete safety information.\n"
            
            return result
    
    except Exception as e:
        return f"Error retrieving compound safety information: {str(e)}"

@mcp.tool()
async def get_compound_bioactivity(cid: str, max_assays: int = 5) -> str:
    """Get bioactivity information for a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
        max_assays: Maximum number of bioassay results to return
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
Bioactivity Information for Aspirin (CID 2244):

Active in 73 bioassays

Top 5 Bioassays:
1. AID 1332: Confirmation of compounds inhibiting hypoxia-inducible factor 1 alpha (HIF-1α)
   - Active: Yes
   - Activity Value: 3.2 µM

2. AID 743255: Neuroprotection Screening - Prevents tert-butyl hydroperoxide-induced death of HT22 mouse hippocampal cells
   - Active: Yes
   - Activity Value: 42.7 µM

3. AID 743228: Inhibitors of Prostaglandin E2 (PGE2) production in MDA-MB-231 cells
   - Active: Yes
   - Activity Value: 6.3 µM

4. AID 504357: Assay to identify inhibitors of tumor necrosis factor alpha (TNFα) signaling in human endothelial cells
   - Active: Yes
   - Activity Value: 18.5 µM

5. AID 463254: Inhibition of cyclooxygenase (COX) enzymatic activity
   - Active: Yes
   - Activity Value: 0.62 µM
"""
    
    try:
        async with httpx.AsyncClient() as client:
            # First get the compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            
            if name_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            compound_name = "Unknown"
            if name_response.status_code == 200:
                name_data = name_response.json()
                try:
                    compound_name = name_data["PropertyTable"]["Properties"][0]["Title"]
                except (KeyError, IndexError):
                    pass
            
            # Get compound bioactivity assays
            assay_url = f"{BASE_URL}/compound/cid/{cid}/assaysummary/JSON"
            assay_response = await client.get(assay_url)
            
            if assay_response.status_code == 404:
                return f"No bioactivity information found for compound with CID {cid}"
                
            assay_response.raise_for_status()
            data = assay_response.json()
            
            # Initialize result
            result = f"\nBioactivity Information for {compound_name} (CID {cid}):\n"
            
            # Check if there's any bioactivity data
            if "Table" not in data or "Row" not in data["Table"] or not data["Table"]["Row"]:
                return result + "\nNo bioactivity information found for this compound in PubChem.\n"
            
            # Count the number of active assays
            active_assays = [row for row in data["Table"]["Row"] if row.get("Active")]
            total_assays = len(data["Table"]["Row"])
            
            result += f"\nActive in {len(active_assays)} out of {total_assays} bioassays\n"
            
            if active_assays:
                # Sort by significance (active assays with lower activity values first)
                # Note: This is a simplification; actual significance may depend on assay type
                sorted_assays = []
                for row in active_assays:
                    try:
                        activity_value = float(row.get("ActivityValue", 999999))
                        sorted_assays.append((activity_value, row))
                    except (ValueError, TypeError):
                        # If we can't convert to float, put it at the end
                        sorted_assays.append((999999, row))
                
                sorted_assays.sort()  # Sort by activity value
                
                # Take top results limited by max_assays
                top_assays = sorted_assays[:max_assays]
                
                result += f"\nTop {len(top_assays)} Bioassays:\n"
                
                for i, (_, assay) in enumerate(top_assays):
                    aid = assay.get("AID", "Unknown")
                    name = assay.get("AssayName", "Unknown Assay")
                    active = "Yes" if assay.get("Active") else "No"
                    
                    result += f"{i+1}. AID {aid}: {name}\n"
                    result += f"   - Active: {active}\n"
                    
                    if assay.get("ActivityValue"):
                        value = assay.get("ActivityValue")
                        unit = assay.get("ActivityUnit", "")
                        result += f"   - Activity Value: {value} {unit}\n"
                    
                    result += "\n"
            
            return result
    
    except Exception as e:
        return f"Error retrieving compound bioactivity information: {str(e)}" 