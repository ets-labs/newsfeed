FROM python:3.7-alpine3.9

ENV PORT=8000

WORKDIR /code
COPY . /code/

ENV PYTHONPATH "${PYTHONPATH}:/code/src/"

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
