FROM python:3.10.12-slim

WORKDIR /app

COPY . .


RUN pip install Flask
RUN pip install Flask-Bootstrap

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0" ]

