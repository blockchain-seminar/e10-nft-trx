# Base image
FROM node:latest

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy local code to the container
COPY . .

# Build the project for production
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Serve the static files
CMD ["serve", "-s", "build", "-l", "3000"]

# Open port 3000
EXPOSE 3000
