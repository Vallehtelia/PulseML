FROM node:20-alpine

ENV FRONTEND_PORT=3000 \
    FRONTEND_HOST=0.0.0.0

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "npm run dev -- --host ${FRONTEND_HOST:-0.0.0.0} --port ${FRONTEND_PORT:-3000}"]


