FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

RUN apk add --no-cache mosquitto

COPY . .

EXPOSE 3001

CMD ["node", "app.js"]
