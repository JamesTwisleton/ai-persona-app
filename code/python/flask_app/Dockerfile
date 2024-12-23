# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local project files into the working directory
COPY . /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    gcc \
    g++ \
    && apt-get clean
    
RUN pip install bottleneck
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install transformers

# Expose the port on which the Dash app runs (default 8050)
EXPOSE 8050

# Define the command to run the app
CMD ["python", "run_app.py"]
