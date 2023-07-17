FROM rasa/rasa-sdk:2.8.11

WORKDIR /app

COPY ./requirements-actions.txt .

USER root

RUN pip install -r requirements-actions.txt

EXPOSE 5055

USER 1001