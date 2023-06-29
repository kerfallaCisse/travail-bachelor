# premade rasa container
FROM rasa/rasa 

USER root

WORKDIR /app

COPY . .

USER 1001

EXPOSE 5005

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api", "--cors='*'"]




