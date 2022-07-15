FROM python:3.10.4-slim-buster

ENV DEBIAN_ENVIRONMENT=noninteractive
RUN echo "Installing system packages and poetry" \
    &&  apt-get update -yqq \
    &&  apt-get install -yqq build-essential vim git curl apache2-utils

WORKDIR /app/
COPY requirements.txt /app/

RUN echo "Installing python project dependencies" \
    && pip install -r requirements.txt


COPY bot_v2.py logs.py secrets.py cities.txt country.txt event_tracker.py /app/
COPY db/ /app/db
COPY telegramcalendar/ /app/telegramcalendar

CMD python bot_v2.py

#HEALTHCHECK --interval=1m CMD curl http://localhost:8000/v1/healthcheck
