FROM rasa/rasa-sdk:2.8.11

WORKDIR /app

COPY . /app/actions
# On copy éventuellement le folder functions qui contient les fonctions dans le container

USER root

RUN pip install -r requirements-actions.txt

EXPOSE 5055
