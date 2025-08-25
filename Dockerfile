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
COPY importmap.json dist/importmap.json
EXPOSE 9000
CMD ["serve", "-s", "dist", "-l", "9000"]


#change port to 8000 before building the docker image 