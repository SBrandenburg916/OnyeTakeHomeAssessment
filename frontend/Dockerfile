# Use an official Node.js image
FROM node:18

# Set working directory inside the container
WORKDIR /app

# Copy package files first and install dependencies
COPY package*.json ./

# Install dependencies (legacy peer deps avoids react-scripts/webpack issues)
RUN npm install --legacy-peer-deps

# Copy the rest of the frontend source code
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY ./src ./src
COPY ./public ./public


# Expose development server port
EXPOSE 3000

# Start the frontend app
CMD ["npm", "start"]
