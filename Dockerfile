FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Run the MCP server
CMD ["python", "src/mcp_memory_bank/main.py"]
