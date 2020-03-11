FROM python:3.7-alpine
LABEL maintainer="Ryan"

ENV PYTHONUNBUFFERED 1
# make requirements
COPY ./requirements.txt /requirements.txt
# apk is the package manager (alpine package manager) to add postgresql no-cache 
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps
# create directory
RUN mkdir /app
WORKDIR /app
COPY ./app /app
# create a user for running applications; need this because this user will run the application and we dont want to use
RUN adduser -D user
USER user