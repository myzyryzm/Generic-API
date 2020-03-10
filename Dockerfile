FROM python:3.7-alpine
LABEL maintainer="Ryan"

ENV PYTHONUNBUFFERED 1
# make requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
# create directory
RUN mkdir /app
WORKDIR /app
COPY ./app /app
# create a user for running applications; need this because this user will run the application and we dont want to use
RUN adduser -D user
USER user