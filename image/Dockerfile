FROM node:alpine as build-stage
WORKDIR /app
COPY ./ ./
RUN npm install
RUN npm run build

FROM nginx:alpine
WORKDIR /app/dist
COPY --from=build-stage /app/dist ./
WORKDIR /app/server
COPY server/*.py ./
RUN apk update
RUN apk add python3
RUN apk add py3-pip
RUN pip3 install --no-cache-dir Flask Flask-Cors mcrcon requests
WORKDIR /app
COPY image/start.sh ./
COPY nginx.conf /etc/nginx
EXPOSE 80
CMD ["/bin/sh", "/app/start.sh"]
