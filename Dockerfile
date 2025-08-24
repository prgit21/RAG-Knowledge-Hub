FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# RUN npm run build

RUN npm run build:webpack \
    && npm run build:types
FROM node:18-slim
WORKDIR /app
RUN npm i -g serve
COPY --from=build /app/dist ./dist
EXPOSE 9000
CMD ["serve", "-s", "dist", "-l", "9000"]
