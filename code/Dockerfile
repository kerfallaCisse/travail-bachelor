FROM python:3.10.12-slim

RUN pip install --upgrade pip
RUN pip install rasa
RUN pip install deep-translator

WORKDIR /app_rasa

COPY . .

RUN rasa train nlu

# We set the user to run, ro avoid runing the application with the root user
USER 1001

# We set the entrypoint for interactive shell
ENTRYPOINT [ "rasa" ]

# We set the command to run while creating the image
CMD [ "run", "--enable-api", "--cors='*'", "--port", "8080" ]


