#!/bin/bash

LOG_CONFIG=logging_config.yml
UVICORN_APP=main:app

if [ "$DEBUG_LEVEL" -gt 0 ]; then
    LOG_CONFIG=logging_config_debug.yml
fi

if [ "$APP_MODE" = "sidecar" ]; then
    UVICORN_APP=sidecar:app
fi

exec uvicorn --host 0.0.0.0 --port 8000 --log-config $LOG_CONFIG $UVICORN_APP
