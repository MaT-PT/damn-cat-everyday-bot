FROM alpine:latest

ARG USER=app

RUN apk add --no-cache --update uv bash \
    && rm -rf ~/.cache/* /usr/local/share/man /tmp/*

RUN adduser -D "${USER}"
USER "${USER}"

COPY --chown="${USER}":"${USER}" . /app
WORKDIR /app

ENV UV_NO_DEV=1
RUN uv sync

ENTRYPOINT ["./run-bot.sh"]
