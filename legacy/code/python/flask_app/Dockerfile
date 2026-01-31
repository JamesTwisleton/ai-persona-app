# Use a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a directory for persistent data
RUN mkdir -p /app/app/data && chmod -R 777 /app/app/data

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the Flask app
EXPOSE 8050

# Define the default command to run the app
CMD ["python", "run_app.py"]
