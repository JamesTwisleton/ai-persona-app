# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local project files into the working directory
COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    gfortran


# Install the dependencies from requirements.txt
RUN pip install numpy==1.23.5 setuptools==75.6.0

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Dash app runs (default 8050)
EXPOSE 8080

# Define the command to run the app
CMD ["python", "app.py"]
