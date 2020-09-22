FROM python:3.8-buster

ENV PORT=8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/code/src/"

WORKDIR /code
COPY . /code/

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

EXPOSE $PORT

CMD ["python", "-m", "newsfeed"]
