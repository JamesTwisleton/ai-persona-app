# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /work_dir

# Copy run_app.py and requirements.txt to the working directory
COPY run_app.py requirements.txt /work_dir/

# Copy the entire app directory into the container
COPY app /work_dir/app

# Install required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    gcc \
    g++ \
    && apt-get clean

# TODO: make base image with all dependencies installed
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the app runs
EXPOSE 8050

# Define the command to run the app
CMD ["python", "run_app.py"]
