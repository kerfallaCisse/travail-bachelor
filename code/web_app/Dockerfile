FROM python:3.10.12-slim

WORKDIR /flask_app

COPY ./app.py .


RUN pip install Flask

EXPOSE 5000


CMD ["flask", "--app", "app", "run", "--host=0.0.0.0" ]
