FROM node:18

WORKDIR /app

RUN npm config set strict-ssl false

COPY package*.json ./

RUN npm install --no-audit --no-fund

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
