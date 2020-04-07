FROM python:3.7-alpine
LABEL maintainer="Ryan"

ENV PYTHONUNBUFFERED 1
# make requirements
COPY ./requirements.txt /requirements.txt
# apk is the package manager (alpine package manager) to add postgresql no-cache 
# shit that we want to keep around for a while
RUN apk add --update --no-cache postgresql-client jpeg-dev
# temp build dependencies so will be deleted when done with them
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps
# create directory
RUN mkdir /app
WORKDIR /app
COPY ./app /app
# store any folders that need to be shared with other containers put them in vol (meaning volume)
# -p means create all directories (if they do not exist)
RUN mkdir -p /vol/web/media
# static is for shit like js
RUN mkdir -p /vol/web/static
# create a user for running applications; need this because this user will run the application and we dont want to use
RUN adduser -D user
# gives ownership of all vol folders and it subdirectories to user
RUN chown -R user:user /vol/
# user can do whatever it want
RUN chmod -R 755 /vol/web
USER user