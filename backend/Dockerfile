FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Docker-in-Docker capability and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -sSL https://get.docker.com/ | sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security (optional but recommended)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Expose FastAPI port
EXPOSE 8000

# Use non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
