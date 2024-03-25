FROM python:3.11-alpine

RUN addgroup --gid 1001 stadtliga && \
    yes | adduser --disabled-password --uid 1001 --ingroup stadtliga stadtliga

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_DEBUG=0

WORKDIR /usr/bin/stadtliga/src
COPY ./src/requirements.txt ./

RUN pip install -r requirements.txt

USER stadtliga

COPY --chown=stadtliga ./src ./

CMD gunicorn --bind 0.0.0.0:8080 run:app
