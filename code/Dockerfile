# premade rasa container
FROM rasa/rasa:3.6.4.dev20230728-full

USER root

WORKDIR /app
WORKDIR /app/models

COPY . .

RUN rasa train

USER 1001

EXPOSE 5005

ENTRYPOINT [ "rasa" ]

CMD ["run","--enable-api","--port","5005"]




