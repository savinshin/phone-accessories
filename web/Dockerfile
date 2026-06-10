FROM node:24-slim

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 4200

CMD ["npm", "start", "--", "--host", "0.0.0.0", "--allowed-hosts", "true", "--proxy-config", "src/proxy.conf.json"]
