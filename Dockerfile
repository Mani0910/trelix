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

# Create uploads directory
RUN mkdir -p uploads

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
