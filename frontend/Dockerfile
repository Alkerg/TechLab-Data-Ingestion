FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/login', (r) => { if (r.statusCode >= 400) throw new Error(r.statusCode) })"

CMD ["node", "app.js"]
