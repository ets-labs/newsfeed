FROM python:3.7-alpine3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/code/src/"

WORKDIR /code
COPY . /code/

RUN apk update \
 && apk upgrade --purge \
 && apk add build-base \
 && pip install --upgrade pip \
 && pip install -r requirements.txt \
 && rm -rf /var/cache/apk/* \
 && rm -rf ~/.cache

CMD ["behave"]
