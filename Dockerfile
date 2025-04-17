FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "pubchem_mcp.server:app", "--host", "0.0.0.0", "--port", "8000"]
