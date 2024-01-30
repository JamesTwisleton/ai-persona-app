FROM node:latest

ARG MONGODB_URI
ARG MONGODB_DB

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Bundle app source inside Docker image
COPY . .

# Check if .env.local exists and copy it if it does
RUN if [ -f .env.local ]; then cp .env.local .env; fi

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD [ "npm", "start" ]
