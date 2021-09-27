FROM python:3.9-alpine
LABEL maintainer="alekceyanatolievich@gmail.com"
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN apk add curl tini
ENV FLASK_APP=diploma_app
ENTRYPOINT ["tini", "--"]
CMD ["flask", "run", "--host", "0.0.0.0"]
HEALTHCHECK --interval=1m --timeout=10s CMD curl --fail http://localhost:5000/healthcheck || kill 1

