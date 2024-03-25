FROM python:3.11-alpine

RUN addgroup --gid 1001 stadtliga && \
    yes | adduser --disabled-password --uid 1001 --ingroup stadtliga stadtliga

RUN apk add curl

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_DEBUG=0

WORKDIR /usr/bin/stadtliga/src
COPY ./src/requirements.txt ./

RUN pip install -r requirements.txt

USER stadtliga

COPY --chown=stadtliga ./src ./

HEALTHCHECK --interval=1h --timeout=30s --retries=5 --start-period=3m --start-interval=10s CMD [ "curl", "localhost:8080/health" ]

CMD gunicorn --bind 0.0.0.0:8080 run:app --access-logfile -
