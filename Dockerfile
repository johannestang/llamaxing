FROM python:3.10

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONUNBUFFERED=1

COPY ./logging_config.yml /app/llamaxing/logging_config.yml
COPY ./logging_config_debug.yml /app/llamaxing/logging_config_debug.yml
COPY ./launch.sh /app/launch.sh
COPY ./llamaxing /app/llamaxing

WORKDIR /app/llamaxing

ENV DEBUG_LEVEL=0

CMD ["/app/launch.sh"]
