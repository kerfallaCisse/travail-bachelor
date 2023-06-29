FROM rasa/rasa-sdk:2.8.11

WORKDIR /app

COPY ./requirements-actions.txt ./

USER root

RUN pip install -r requirements-actions.txt

COPY . /app/actions
COPY ../data /app/data
COPY ../funtions /app/functions

USER 1001