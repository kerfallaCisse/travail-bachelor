# premade rasa container
FROM rasa/rasa

USER root

WORKDIR /app

COPY . .

RUN rasa train

USER 1001

EXPOSE 5005

ENTRYPOINT [ "rasa" ]




