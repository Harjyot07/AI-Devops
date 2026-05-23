FROM node:18

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --no-audit --no-fund

# Verify express is installed (backend dependency)
#RUN ls node_modules/express/package.json

# Copy source code
COPY . .

EXPOSE 3001
CMD ["node", "server.js"]
