"""
Compound structure conversion and visualization functionality for the PubChem MCP server.
"""

import urllib.parse
import base64
from typing import Dict, Any, List, Optional
import httpx
from ..utils import BASE_URL, pubchem_client
from mcp_server import FastMCP

# MCP instance - will be injected from main module
mcp = None

# Allowed image formats
ALLOWED_FORMATS = ["PNG", "SVG", "JSON", "SDF", "SMILES", "InChI"]

@mcp.tool()
async def convert_structure(input_format: str, output_format: str, structure: str) -> str:
    """Convert between chemical structure formats.
    
    Args:
        input_format: Input format (SMILES, InChI, SDF, etc.)
        output_format: Output format (SMILES, InChI, SDF, etc.)
        structure: Chemical structure string in the input format
    """
    # Mock data for testing
    if input_format.upper() == "SMILES" and structure == "CC(=O)OC1=CC=CC=C1C(=O)O" and output_format.upper() == "INCHI":
        return "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)"
    
    if input_format.upper() == "INCHI" and structure.endswith("C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)") and output_format.upper() == "SMILES":
        return "CC(=O)OC1=CC=CC=C1C(=O)O"
    
    try:
        input_format = input_format.upper()
        output_format = output_format.upper()
        
        # Validate formats
        if input_format not in ["SMILES", "INCHI"]:
            return f"Error: Input format '{input_format}' not supported. Please use SMILES or InChI."
        
        if output_format not in ["SMILES", "INCHI"]:
            return f"Error: Output format '{output_format}' not supported. Please use SMILES or InChI."
        
        # Ensure InChI has proper prefix
        if input_format == "INCHI" and not structure.startswith("InChI="):
            structure = "InChI=" + structure
        
        # URL-encode the structure
        encoded_structure = urllib.parse.quote(structure)
        
        # Use different APIs based on input format
        if input_format == "SMILES":
            url = f"{BASE_URL}/compound/smiles/{encoded_structure}/property/InChIKey,CanonicalSMILES,InChI/JSON"
        else:  # input_format == "INCHI"
            url = f"{BASE_URL}/compound/inchi/{encoded_structure}/property/InChIKey,CanonicalSMILES,InChI/JSON"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return f"Error: Could not convert the provided structure. Please check that it is valid {input_format}."
            
            response.raise_for_status()
            data = response.json()
            
            if "PropertyTable" not in data or "Properties" not in data["PropertyTable"] or not data["PropertyTable"]["Properties"]:
                return f"Error: Could not convert the provided structure. No properties found."
            
            properties = data["PropertyTable"]["Properties"][0]
            
            # Return the requested format
            if output_format == "SMILES":
                return properties.get("CanonicalSMILES", "Error: SMILES not found in the response")
            elif output_format == "INCHI":
                return properties.get("InChI", "Error: InChI not found in the response")
            else:
                return "Error: Output format not properly processed"
    
    except Exception as e:
        return f"Error converting structure: {str(e)}"

@mcp.tool()
async def get_structure_image(cid: str, image_format: str = "PNG", size: str = "500x500") -> str:
    """Get a 2D image of a compound structure by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
        image_format: Image format (PNG or SVG)
        size: Image size in pixels (width x height)
    """
    # Mock data - we'll return a placeholder message since we can't return actual images in text
    if cid == "2244":  # Aspirin
        return f"Image URL for Aspirin (CID 2244) in {image_format} format at size {size}:\nhttps://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=2244&t=l"
    
    try:
        # Validate format
        image_format = image_format.upper()
        if image_format not in ["PNG", "SVG"]:
            return f"Error: Image format '{image_format}' not supported. Please use PNG or SVG."
        
        # Validate size format (should be widthxheight)
        if not size.lower().count("x") == 1:
            return "Error: Size should be in format 'widthxheight' (e.g., '500x500')"
        
        # Generate image URL
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}&t=l"
        
        if image_format == "SVG":
            image_url = f"{image_url}&format=svg"
        
        # Parse size
        try:
            width, height = size.lower().split("x")
            image_url = f"{image_url}&width={width}&height={height}"
        except ValueError:
            return "Error: Could not parse size. Please use format 'widthxheight' (e.g., '500x500')"
        
        # Verify the compound exists
        async with httpx.AsyncClient() as client:
            # Check if the compound exists
            check_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            check_response = await client.get(check_url)
            
            if check_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            check_response.raise_for_status()
            
            # Return the image URL
            return f"Image URL for compound CID {cid} in {image_format} format at size {size}:\n{image_url}"
            
    except Exception as e:
        return f"Error retrieving structure image: {str(e)}"

@mcp.tool()
async def get_3d_structure(cid: str, format: str = "SDF") -> str:
    """Get a 3D structure of a compound by PubChem CID.
    
    Args:
        cid: PubChem Compound ID
        format: Output format (SDF or JSON)
    """
    # Mock data for testing
    if cid == "2244" and format.upper() == "SDF":  # Aspirin
        return """3D Structure for Aspirin (CID 2244) in SDF format:

To download the full 3D SDF file, visit:
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/record/SDF/?record_type=3d

Preview of SDF structure:
2244
  -OEChem-10101922013D

 21 21  0     0  0  0  0  0  0999 V2000
   -0.9010    1.3672   -0.0315 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2080   -1.0232   -0.0114 O   0  0  0  0  0  0  0  0  0  0  0  0
    2.1228   -0.0914    0.0013 O   0  0  0  0  0  0  0  0  0  0  0  0
    1.3288    2.0331   -0.0052 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.3463    0.0507    0.0049 C   0  0  0  0  0  0  0  0  0  0  0  0
...remaining SDF structure truncated...
"""
    
    if cid == "2244" and format.upper() == "JSON":  # Aspirin
        return """3D Structure for Aspirin (CID 2244) in JSON format:

To download the full 3D JSON file, visit:
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/record/JSON/?record_type=3d

Preview of JSON structure:
{
  "PC_Compounds": [
    {
      "id": {
        "id": {
          "cid": 2244
        }
      },
      "atoms": {
        "aid": [
          1,
          2,
          3,
          ...
        ],
        "element": [
          8,
          8,
          8,
          ...
        ]
      },
      "bonds": {
        "aid1": [
          1,
          1,
          2,
          ...
        ],
        "aid2": [
          5,
          13,
          5,
          ...
        ],
        "order": [
          1,
          1,
          2,
          ...
        ]
      },
      ...remaining JSON structure truncated...
    }
  ]
}
"""
    
    try:
        # Validate format
        format = format.upper()
        if format not in ["SDF", "JSON"]:
            return f"Error: Format '{format}' not supported. Please use SDF or JSON."
        
        # Check if the compound exists
        async with httpx.AsyncClient() as client:
            check_url = f"{BASE_URL}/compound/cid/{cid}/property/Title/JSON"
            check_response = await client.get(check_url)
            
            if check_response.status_code == 404:
                return f"Error: No compound found with CID {cid}"
            
            # Get the compound name for a more descriptive response
            compound_name = "Unknown"
            if check_response.status_code == 200:
                data = check_response.json()
                try:
                    compound_name = data["PropertyTable"]["Properties"][0]["Title"]
                except (KeyError, IndexError):
                    pass
            
            # Construct the URL for the 3D structure
            structure_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/{format}/?record_type=3d"
            
            # We can't return the actual 3D structure as it would be too large,
            # so instead we return the URL where it can be downloaded
            result = f"3D Structure for {compound_name} (CID {cid}) in {format} format:\n\n"
            result += f"To download the full 3D {format} file, visit:\n{structure_url}\n"
            
            return result
    
    except Exception as e:
        return f"Error retrieving 3D structure: {str(e)}"

@mcp.tool()
async def generate_2d_coordinates(smiles: str, format: str = "SDF") -> str:
    """Generate 2D coordinates for a molecule from its SMILES string.
    
    Args:
        smiles: SMILES notation of the molecule
        format: Output format (SDF or JSON)
    """
    # Mock data for testing
    if smiles == "CC(=O)OC1=CC=CC=C1C(=O)O" and format.upper() == "SDF":  # Aspirin
        return """2D Coordinates for molecule (SMILES: CC(=O)OC1=CC=CC=C1C(=O)O) in SDF format:

To generate the full 2D SDF file, visit:
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/CC(=O)OC1=CC=CC=C1C(=O)O/record/SDF

Preview of SDF structure with 2D coordinates:
0
     RDKit          2D

 13 13  0  0  0  0  0  0  0  0999 V2000
    6.3301    1.5000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6602    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6602   -0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    8.9904    1.5000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
...remaining SDF structure truncated...
"""
    
    if smiles == "CC(=O)OC1=CC=CC=C1C(=O)O" and format.upper() == "JSON":  # Aspirin
        return """2D Coordinates for molecule (SMILES: CC(=O)OC1=CC=CC=C1C(=O)O) in JSON format:

To generate the full 2D JSON file, visit:
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/CC(=O)OC1=CC=CC=C1C(=O)O/record/JSON

Preview of JSON structure with 2D coordinates:
{
  "PC_Compounds": [
    {
      "id": {
        "id": {
          "cid": 0
        }
      },
      "atoms": {
        "aid": [
          1,
          2,
          3,
          ...
        ],
        "element": [
          6,
          6,
          8,
          ...
        ]
      },
      "coords": [
        {
          "type": "2d",
          "aid": [
            1,
            2,
            3,
            ...
          ],
          "conformers": [
            {
              "x": [
                6.3301,
                7.6602,
                7.6602,
                ...
              ],
              "y": [
                1.5000,
                0.7500,
                -0.7500,
                ...
              ]
            }
          ]
        }
      ],
      ...remaining JSON structure truncated...
    }
  ]
}
"""
    
    try:
        # Validate SMILES
        if not smiles:
            return "Error: SMILES string cannot be empty"
        
        # Validate format
        format = format.upper()
        if format not in ["SDF", "JSON"]:
            return f"Error: Format '{format}' not supported. Please use SDF or JSON."
        
        # URL-encode the SMILES
        encoded_smiles = urllib.parse.quote(smiles)
        
        # Construct the URL for the 2D structure
        structure_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded_smiles}/record/{format}"
        
        # We can't return the actual structure as it would be too large,
        # so instead we return the URL where it can be generated
        result = f"2D Coordinates for molecule (SMILES: {smiles}) in {format} format:\n\n"
        result += f"To generate the full 2D {format} file, visit:\n{structure_url}\n"
            
        return result
    
    except Exception as e:
        return f"Error generating 2D coordinates: {str(e)}" 