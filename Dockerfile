# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Healthcheck helper
RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY config.py .
COPY mxone_trelix.py .
COPY mivb_trelix.py .
COPY mbg_trelix.py .
COPY miv5000_trelix.py .
COPY index.html .
COPY fireeye.sh .
COPY trelix_cli.py .
COPY README_NEW.md README.md
COPY FEATURES_NEW.md FEATURES.md

# Make CLI tool executable and installable
RUN chmod +x trelix_cli.py && \
    ln -s /app/trelix_cli.py /usr/local/bin/trelix-cli

# Create uploads directory
RUN mkdir -p uploads

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

# Run Flask app
CMD ["python", "app.py"]
