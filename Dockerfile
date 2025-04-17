FROM python:3.10-slim

WORKDIR /app

# Copy required files for pip installation
COPY pyproject.toml README.md LICENSE ./

# Copy the source code
COPY mcp_server/ ./mcp_server/

# Install the package
RUN pip install --no-cache-dir -e .

# Install production dependencies
RUN pip install --no-cache-dir fastapi httpx mcp pydantic uvicorn

# Run the MCP server in stdio mode
CMD ["python", "-m", "mcp_server", "--stdio"] 