FROM bash:latest

WORKDIR /artefact-handler

RUN apk add wget

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc &&\
    chmod +x mc &&\
    mv mc /usr/local/bin/mc
