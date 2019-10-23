FROM python:3.7-alpine3.9

ENV PORT=8000
ENV API_BASE_PATH="/"
ENV MAX_NEWSFEEDS="1024"
ENV EVENTS_QUEUE_SIZE="16"
ENV EVENTS_PER_NEWSFEED="1024"
ENV SUBSCRIPTIONS_PER_NEWSFEED="1024"
ENV NEWSFEED_ID_LENGTH="128"
ENV PROCESSOR_CONCURRENCY="4"

WORKDIR /code
COPY . /code/

ENV PYTHONPATH="${PYTHONPATH}:/code/src/"

RUN apk update \
 && apk upgrade --purge \
 && apk add build-base \
 && apk add tini \
 && apk add libffi libffi-dev \
 && pip install -r requirements.txt \
 && rm -rf /var/cache/apk/* \
 && rm -rf ~/.cache

EXPOSE $PORT

CMD ["python", "-m", "newsfeed.app.main"]
