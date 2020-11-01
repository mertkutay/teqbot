FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y gettext \
  && apt-get install -y ffmpeg \
  && apt-get install -y opus-tools \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements* /
RUN pip install --use-feature=2020-resolver -r /requirements.txt

COPY ./compose/production/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY . /app

WORKDIR /app

CMD ["/start"]
