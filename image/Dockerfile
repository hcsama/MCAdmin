FROM python:3-alpine
WORKDIR /usr/src/app
COPY ./ ./
RUN pip install Flask Flask-Cors mcrcon
RUN apk add --update npm
RUN npm install
# RUN npm run-script build
EXPOSE 8080
EXPOSE 5000
CMD ["/bin/sh", "/usr/src/app/image/start.sh"]
