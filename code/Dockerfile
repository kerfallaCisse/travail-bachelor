# premade rasa container
FROM rasa/rasa 

USER root

WORKDIR /app

COPY . .

USER 1001

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api", "--cors='*'", "--port", "5005"]




