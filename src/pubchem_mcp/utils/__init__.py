"""
Utility classes and functions for the PubChem MCP server.
"""

import urllib.parse
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from functools import lru_cache

# Base URL for PubChem API
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

class RateLimiter:
    """Simple rate limiter to avoid overloading the PubChem API."""
    
    def __init__(self, calls_per_second: float = 5.0):
        """Initialize the rate limiter.
        
        Args:
            calls_per_second: Maximum number of calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire the rate limiter."""
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.min_interval:
                await asyncio.sleep(self.min_interval - time_since_last_call)
            
            self.last_call_time = asyncio.get_event_loop().time()

class PubChemClient:
    """Base client for interacting with the PubChem API."""
    
    def __init__(self, rate_limit: float = 5.0, timeout: float = 10.0):
        """Initialize the PubChem client.
        
        Args:
            rate_limit: Maximum number of calls per second
            timeout: Request timeout in seconds
        """
        self.rate_limiter = RateLimiter(rate_limit)
        self.timeout = timeout
        self._cache = {}
    
    async def get(self, url: str, cache_key: Optional[str] = None, cache_ttl: int = 3600) -> httpx.Response:
        """Make a GET request to the PubChem API with rate limiting and caching.
        
        Args:
            url: URL to request
            cache_key: Key for caching the response (if None, URL is used)
            cache_ttl: Cache time-to-live in seconds
        
        Returns:
            Response object
        """
        # Check cache
        cache_key = cache_key or url
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            # If cache entry is still valid, return it
            if asyncio.get_event_loop().time() - entry['time'] < cache_ttl:
                return entry['response']
        
        # Acquire rate limiter to prevent too many requests
        await self.rate_limiter.acquire()
        
        # Make the actual request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            
            # Cache successful responses
            if response.status_code == 200:
                self._cache[cache_key] = {
                    'time': asyncio.get_event_loop().time(),
                    'response': response
                }
            
            return response
    
    @staticmethod
    def format_response(title: str, data: List[str], show_count: bool = False) -> str:
        """Format a list of data items into a readable text response.
        
        Args:
            title: Title for the response
            data: List of data items to format
            show_count: Whether to show the count of items
        
        Returns:
            Formatted text response
        """
        result = f"{title}\n"
        
        for i, item in enumerate(data, 1):
            result += f"{i}. {item}\n"
        
        if show_count:
            result += f"\nTotal items: {len(data)}"
        
        return result
    
    @staticmethod
    def format_table(title: str, headers: List[str], rows: List[List[str]], 
                     col_widths: Optional[List[int]] = None) -> str:
        """Format data as a table.
        
        Args:
            title: Title for the table
            headers: Column headers
            rows: Table data rows
            col_widths: Optional column widths (auto-calculated if None)
        
        Returns:
            Formatted table as string
        """
        # Calculate column widths if not provided
        if col_widths is None:
            col_widths = []
            for i in range(len(headers)):
                col_width = len(headers[i])
                for row in rows:
                    if i < len(row):
                        col_width = max(col_width, len(str(row[i])))
                col_widths.append(col_width + 2)  # Add padding
        
        # Create header row
        result = f"{title}\n"
        separator = "-" * (sum(col_widths) + len(headers) - 1) + "\n"
        result += separator
        
        header_row = ""
        for i, header in enumerate(headers):
            header_row += f"{header:<{col_widths[i]}}"
            if i < len(headers) - 1:
                header_row += " | "
        result += header_row + "\n"
        result += separator
        
        # Create data rows
        for row in rows:
            data_row = ""
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    data_row += f"{str(cell):<{col_widths[i]}}"
                    if i < len(row) - 1 and i < len(headers) - 1:
                        data_row += " | "
            result += data_row + "\n"
        
        return result

# Common property mapping for compounds
PROPERTY_MAP = {
    "molecularweight": "MolecularWeight",
    "mw": "MolecularWeight",
    "weight": "MolecularWeight",
    "xlogp": "XLogP",
    "logp": "XLogP",
    "tpsa": "TPSA",
    "hbonddonorcount": "HBondDonorCount",
    "hbd": "HBondDonorCount",
    "hbondacceptorcount": "HBondAcceptorCount",
    "hba": "HBondAcceptorCount",
    "rotatiblebondcount": "RotatableBondCount",
    "rb": "RotatableBondCount",
    "formula": "MolecularFormula",
    "inchi": "InChI",
    "inchikey": "InChIKey",
    "canonicalsmiles": "CanonicalSMILES",
    "smiles": "CanonicalSMILES",
}

# Create a singleton instance for shared use
pubchem_client = PubChemClient() 