FROM python:3.9-alpine
LABEL maintainer="alekceyanatolievich@gmail.com"
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENV FLASK_APP=diploma-app
CMD ["flask", "run", "--host", "0.0.0.0"]
