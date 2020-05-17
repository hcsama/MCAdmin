FROM python:3-alpine
WORKDIR /usr/src/app
COPY ../server ./
RUN pip install Flask Flask-Cors mcrcon
RUN mkdir web
COPY ../src web
RUN npm install
EXPOSE 5000
COPY ./start.sh .
CMD ["/bin/sh", "start.sh"]
