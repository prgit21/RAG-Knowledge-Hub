# Use node:18-alpine base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 9000

# Set production environment
ENV NODE_ENV=production

# Start the application
CMD ["npm", "start"]
