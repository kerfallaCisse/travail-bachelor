# premade rasa container
# FROM rasa/rasa:3.6.2-full
FROM rasa/rasa:3.5.4-full

USER root

WORKDIR /app

RUN pip install sanic

COPY . .

RUN rasa train

VOLUME /app
VOLUME /app/data
VOLUME /app/models

USER 1001

EXPOSE 5005

ENTRYPOINT [ "rasa" ]

CMD [ "run", "-m", "/app/models/", "--enable-api", "--cors='*'"]




