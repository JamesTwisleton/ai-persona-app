# Use the latest Node.js image as the base
FROM node:latest

# Define build-time arguments for MongoDB connection
ARG MONGODB_URI
ARG MONGODB_DB

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json for npm install
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire project to the container
COPY . .

# Check if .env.local exists and copy it to .env if it does
# This allows for local environment variables to be used in the container
RUN if [ -f .env.local ]; then cp .env.local .env; fi

# Set environment variables for MongoDB
# TODO: Remove this workaround once a better solution is implemented
# Currently, NextJS requires these values at build time to check static routes
ENV MONGODB_URI="placeholder_value" \
    MONGODB_DB="placeholder_value"

# Build the Next.js application
RUN npm run build

# Expose port 3000 for the application
EXPOSE 3000

# Command to run the application
CMD [ "npm", "start" ]
