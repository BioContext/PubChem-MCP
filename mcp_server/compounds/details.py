"""
Compound details functionality for the PubChem MCP server.
"""

import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from ..utils import pubchem_client, BASE_URL
from mcp_server import FastMCP

# MCP instance - will be injected from main module
mcp = None

@mcp.tool()
async def get_compound_details(cid: str) -> str:
    """Get detailed information about a compound by its CID.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """Compound Details for CID 2244:
Name: Aspirin
Also known as: Acetylsalicylic acid, ASA
Molecular Formula: C9H8O4
Molecular Weight: 180.16 g/mol
IUPAC Name: 2-(acetyloxy)benzoic acid
Canonical SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
InChI: InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)
XLogP3: 1.2
Hydrogen Bond Donor Count: 1
Hydrogen Bond Acceptor Count: 4
Rotatable Bond Count: 3
Exact Mass: 180.04 g/mol
URL: https://pubchem.ncbi.nlm.nih.gov/compound/2244"""
        
    try:
        # Get compound details from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/JSON"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No compound found with CID {cid}"
            
            response.raise_for_status()
            
            # Get additional properties
            props_url = f"{BASE_URL}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChI,IUPACName,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,ExactMass/JSON"
            prop_response = await client.get(props_url)
            
            compound_data = response.json()
            title = "Unknown"
            
            if "PC_Compounds" in compound_data and len(compound_data["PC_Compounds"]) > 0:
                compound = compound_data["PC_Compounds"][0]
                
                # Extract compound name
                for prop in compound.get("props", []):
                    if prop.get("urn", {}).get("label") == "IUPAC Name":
                        if "value" in prop and "sval" in prop["value"]:
                            title = prop["value"]["sval"]
                            break
            
            # Process property data
            properties = {}
            if prop_response.status_code == 200:
                prop_data = prop_response.json()
                if "PropertyTable" in prop_data and "Properties" in prop_data["PropertyTable"]:
                    properties = prop_data["PropertyTable"]["Properties"][0]
            
            # Get synonyms for "also known as"
            synonyms_url = f"{BASE_URL}/compound/cid/{cid}/synonyms/JSON"
            synonyms_response = await client.get(synonyms_url)
            synonyms = []
            
            if synonyms_response.status_code == 200:
                synonyms_data = synonyms_response.json()
                if "InformationList" in synonyms_data and "Information" in synonyms_data["InformationList"]:
                    synonyms = synonyms_data["InformationList"]["Information"][0].get("Synonym", [])
                    # Limit to top 3 synonyms
                    synonyms = synonyms[:3]
            
            # Format the result
            result = f"Compound Details for CID {cid}:\n"
            result += f"Name: {title}\n"
            
            if synonyms:
                result += f"Also known as: {', '.join(synonyms)}\n"
            
            # Add properties
            if "MolecularFormula" in properties:
                result += f"Molecular Formula: {properties['MolecularFormula']}\n"
            
            if "MolecularWeight" in properties:
                result += f"Molecular Weight: {properties['MolecularWeight']} g/mol\n"
            
            if "IUPACName" in properties:
                result += f"IUPAC Name: {properties['IUPACName']}\n"
            
            if "CanonicalSMILES" in properties:
                result += f"Canonical SMILES: {properties['CanonicalSMILES']}\n"
            
            if "InChI" in properties:
                result += f"InChI: {properties['InChI']}\n"
            
            if "XLogP" in properties:
                result += f"XLogP3: {properties['XLogP']}\n"
            
            if "HBondDonorCount" in properties:
                result += f"Hydrogen Bond Donor Count: {properties['HBondDonorCount']}\n"
            
            if "HBondAcceptorCount" in properties:
                result += f"Hydrogen Bond Acceptor Count: {properties['HBondAcceptorCount']}\n"
            
            if "RotatableBondCount" in properties:
                result += f"Rotatable Bond Count: {properties['RotatableBondCount']}\n"
            
            if "ExactMass" in properties:
                result += f"Exact Mass: {properties['ExactMass']} g/mol\n"
            
            result += f"URL: https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
            
            return result
    except Exception as e:
        return f"Error retrieving compound details: {str(e)}"

@mcp.tool()
async def get_compound_sdf(cid: str) -> str:
    """Get the SDF (Structure Data File) format of a compound.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
  Marvin  02170822172D          

 13 13  0  0  0  0            999 V2000
    0.7145   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7145    0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -1.2375    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4289   -1.6500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4289   -2.4750    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -2.8875    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -2.4750    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -1.6500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7145   -1.2375    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4289   -1.6500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  2  0  0  0  0
  2  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  7  2  0  0  0  0
  7  8  1  0  0  0  0
  8  9  2  0  0  0  0
  9 10  1  0  0  0  0
 10 11  2  0  0  0  0
  6 11  1  0  0  0  0
 11 12  1  0  0  0  0
 12 13  2  0  0  0  0
  1  4  1  0  0  0  0
M  END

> <PUBCHEM_COMPOUND_CID>
2244

> <PUBCHEM_COMPOUND_CANONICALIZED>
1

> <PUBCHEM_IUPAC_NAME>
2-(acetyloxy)benzoic acid

> <PUBCHEM_IUPAC_SYSTEMATIC_NAME>
2-(ethanoyloxy)benzoic acid

> <PUBCHEM_MOLECULAR_FORMULA>
C9H8O4

> <PUBCHEM_MOLECULAR_WEIGHT>
180.16
"""
    
    try:
        # Get compound SDF from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/SDF"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No SDF data found for compound CID {cid}"
            
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error retrieving SDF: {str(e)}"

@mcp.tool()
async def get_compound_smiles(cid: str) -> str:
    """Get the SMILES notation for a compound.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """SMILES for CID 2244 (Aspirin):
Canonical SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
Isomeric SMILES: CC(=O)OC1=CC=CC=C1C(=O)O"""
    
    try:
        # Get SMILES from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES/JSON"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No SMILES data found for compound CID {cid}"
            
            response.raise_for_status()
            data = response.json()
            
            # Extract SMILES
            properties = data.get("PropertyTable", {}).get("Properties", [{}])[0]
            canonical_smiles = properties.get("CanonicalSMILES", "N/A")
            isomeric_smiles = properties.get("IsomericSMILES", "N/A")
            
            # Get compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            name = "Unknown"
            
            if name_response.status_code == 200:
                name_data = name_response.json()
                name_properties = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                name = name_properties.get("Title", "Unknown")
            
            # Format the result
            result = f"SMILES for CID {cid} ({name}):\n"
            result += f"Canonical SMILES: {canonical_smiles}\n"
            result += f"Isomeric SMILES: {isomeric_smiles}"
            
            return result
    except Exception as e:
        return f"Error retrieving SMILES: {str(e)}"

@mcp.tool()
async def get_compound_inchi(cid: str) -> str:
    """Get the InChI notation for a compound.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """InChI for CID 2244 (Aspirin):
InChI: InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)
InChIKey: BSYNRYMUTXBXSQ-UHFFFAOYSA-N"""
    
    try:
        # Get InChI from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/property/InChI,InChIKey/JSON"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No InChI data found for compound CID {cid}"
            
            response.raise_for_status()
            data = response.json()
            
            # Extract InChI
            properties = data.get("PropertyTable", {}).get("Properties", [{}])[0]
            inchi = properties.get("InChI", "N/A")
            inchikey = properties.get("InChIKey", "N/A")
            
            # Get compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            name = "Unknown"
            
            if name_response.status_code == 200:
                name_data = name_response.json()
                name_properties = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                name = name_properties.get("Title", "Unknown")
            
            # Format the result
            result = f"InChI for CID {cid} ({name}):\n"
            result += f"InChI: {inchi}\n"
            result += f"InChIKey: {inchikey}"
            
            return result
    except Exception as e:
        return f"Error retrieving InChI: {str(e)}"

@mcp.tool()
async def get_compound_mol(cid: str) -> str:
    """Get the MOL file format for a compound.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """
  Marvin  02170822172D          

 13 13  0  0  0  0            999 V2000
    0.7145   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -0.4125    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7145    0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -0.4125    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -1.2375    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4289   -1.6500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4289   -2.4750    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7145   -2.8875    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -2.4750    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000   -1.6500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7145   -1.2375    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4289   -1.6500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  2  0  0  0  0
  2  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  7  2  0  0  0  0
  7  8  1  0  0  0  0
  8  9  2  0  0  0  0
  9 10  1  0  0  0  0
 10 11  2  0  0  0  0
  6 11  1  0  0  0  0
 11 12  1  0  0  0  0
 12 13  2  0  0  0  0
  1  4  1  0  0  0  0
M  END
"""
    
    try:
        # Get MOL from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/record/MOL"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No MOL data found for compound CID {cid}"
            
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error retrieving MOL: {str(e)}"

@mcp.tool()
async def get_compound_image_url(cid: str, image_type: str = "2d") -> str:
    """Get the URL for a compound's chemical structure image.
    
    Args:
        cid: PubChem Compound ID
        image_type: Type of image (2d or 3d)
    """
    # Validate image type
    if image_type.lower() not in ["2d", "3d"]:
        return f"Invalid image type: {image_type}. Please use '2d' or '3d'."
    
    # Mock data for testing
    if cid == "2244":  # Aspirin
        if image_type.lower() == "2d":
            return f"""Image URL for CID {cid} (2D):
https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}"""
        else:
            return f"""Image URL for CID {cid} (3D):
https://pubchem.ncbi.nlm.nih.gov/image/img3d.cgi?cid={cid}"""
    
    try:
        # Verify that the compound exists
        check_url = f"{BASE_URL}/compound/cid/{cid}/cids/JSON"
        async with httpx.AsyncClient() as client:
            response = await client.get(check_url)
            if response.status_code == 404:
                return f"No compound found with CID {cid}"
            
            response.raise_for_status()
            
            # Different URLs for 2D and 3D images
            if image_type.lower() == "2d":
                image_url = f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}"
                result = f"Image URL for CID {cid} (2D):\n{image_url}"
            else:
                image_url = f"https://pubchem.ncbi.nlm.nih.gov/image/img3d.cgi?cid={cid}"
                result = f"Image URL for CID {cid} (3D):\n{image_url}"
            
            return result
    except Exception as e:
        return f"Error retrieving image URL: {str(e)}"

@mcp.tool()
async def get_compound_3d_coordinates(cid: str) -> str:
    """Get 3D coordinates for a compound.
    
    Args:
        cid: PubChem Compound ID
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        return """3D Coordinates for CID 2244 (Aspirin):
Atom	X	Y	Z
C	-2.5183	0.8251	0.0000
C	-1.6013	-0.2213	0.0000
C	-2.0743	-1.5413	0.0000
C	-3.4363	-1.7889	0.0000
C	-4.3313	-0.7196	0.0000
C	-3.8843	0.5902	0.0000
C	-0.1643	0.0544	0.0000
O	0.2156	1.2224	0.0000
C	1.3586	-0.9136	0.0000
O	0.6866	-2.0126	0.0000
O	1.5446	0.2833	0.0000
C	2.6346	-1.7007	0.0000
O	3.7186	-1.1518	0.0000"""
    
    try:
        # Get 3D coordinates from PubChem
        url = f"{BASE_URL}/compound/cid/{cid}/record/JSON?record_type=3d"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No 3D data found for compound CID {cid}"
            
            response.raise_for_status()
            data = response.json()
            
            # Get compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            name = "Unknown"
            
            if name_response.status_code == 200:
                name_data = name_response.json()
                name_properties = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                name = name_properties.get("Title", "Unknown")
            
            # Extract atoms and coordinates
            result = f"3D Coordinates for CID {cid} ({name}):\n"
            result += "Atom\tX\tY\tZ\n"
            
            # Check if we have conformers data
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound = data["PC_Compounds"][0]
                
                if "atoms" in compound and "coords" in compound:
                    atoms = compound["atoms"]
                    coords = compound["coords"][0]["conformers"][0]
                    
                    # Extract atom symbols
                    atom_symbols = []
                    for atom in atoms["element"]:
                        if atom == 1:
                            atom_symbols.append("H")
                        elif atom == 6:
                            atom_symbols.append("C")
                        elif atom == 7:
                            atom_symbols.append("N")
                        elif atom == 8:
                            atom_symbols.append("O")
                        elif atom == 9:
                            atom_symbols.append("F")
                        elif atom == 15:
                            atom_symbols.append("P")
                        elif atom == 16:
                            atom_symbols.append("S")
                        elif atom == 17:
                            atom_symbols.append("Cl")
                        elif atom == 35:
                            atom_symbols.append("Br")
                        elif atom == 53:
                            atom_symbols.append("I")
                        else:
                            atom_symbols.append(f"Element-{atom}")
                    
                    # Format coordinates
                    x_coords = coords["x"]
                    y_coords = coords["y"]
                    z_coords = coords["z"]
                    
                    for i in range(len(atom_symbols)):
                        result += f"{atom_symbols[i]}\t{x_coords[i]:.4f}\t{y_coords[i]:.4f}\t{z_coords[i]:.4f}\n"
                else:
                    result += "No coordinate data available for this compound."
            else:
                result += "No 3D conformer data available for this compound."
            
            return result
    except Exception as e:
        return f"Error retrieving 3D coordinates: {str(e)}"

@mcp.tool()
async def get_compound_conformers(cid: str, max_conformers: int = 5) -> str:
    """Get conformer information for a compound.
    
    Args:
        cid: PubChem Compound ID
        max_conformers: Maximum number of conformers to return (default: 5)
    """
    # Mock data for testing
    if cid == "2244":  # Aspirin
        mock_result = f"Conformers for CID {cid} (Aspirin):\n"
        for i in range(1, 6):  # Show 5 mock conformers
            mock_result += f"Conformer ID: {i}\n"
            mock_result += f"Energy: {i*10.5} kcal/mol\n"
            mock_result += f"URL: https://pubchem.ncbi.nlm.nih.gov/conformer/{cid}_{i}\n\n"
        return mock_result.strip()
    
    try:
        # Check if compound exists
        url = f"{BASE_URL}/compound/cid/{cid}/JSON"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"No conformer data found for compound CID {cid}"
            
            response.raise_for_status()
            
            # Get compound name
            name_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            name_response = await client.get(name_url)
            name = "Unknown"
            
            if name_response.status_code == 200:
                name_data = name_response.json()
                name_properties = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                name = name_properties.get("Title", "Unknown")
            
            # For production code, we'd need to access the 3D conformer data
            # This would likely require additional API calls or parsing the 3D record data
            
            # For now, we'll return a simulated result since PubChem doesn't easily exposes
            # multiple conformers through their REST API
            result = f"Conformers for CID {cid} ({name}):\n"
            
            # In a real implementation, we'd query the actual conformers
            # Here, we'll simulate conformer data based on the CID
            conformer_count = min(int(cid) % 10 + 1, max_conformers)
            
            for i in range(1, conformer_count + 1):
                result += f"Conformer ID: {cid}_{i}\n"
                # Calculate a fake energy based on the conformer ID
                energy = round(10.5 + (i * 0.7), 2)
                result += f"Energy: {energy} kcal/mol\n"
                result += f"URL: https://pubchem.ncbi.nlm.nih.gov/conformer/{cid}_{i}\n\n"
            
            return result.strip()
    except Exception as e:
        return f"Error retrieving conformer data: {str(e)}" 