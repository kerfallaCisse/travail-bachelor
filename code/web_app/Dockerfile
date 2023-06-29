FROM python:3.10.12-slim

WORKDIR /flask_app

COPY ./app.py .


RUN pip install Flask
RUN pip install Flask-Bootstrap

EXPOSE 5001

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0" ]

