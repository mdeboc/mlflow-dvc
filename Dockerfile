FROM python:3.7.9-slim-buster

RUN apt update \
    && apt install -y --no-install-recommends \
    curl \
    ca-certificates \
    bash-completion \
    libgomp1 \
    g++ \
    gcc \
    make \
    git \
    libopenblas-dev \
    python3-tk \
    && apt autoremove -y \
    && apt autoclean \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
ENV POETRY_CACHE /work/.cache/poetry
RUN $HOME/.poetry/bin/poetry config virtualenvs.path $POETRY_CACHE
ENV PATH /root/.poetry/bin:/bin:/usr/local/bin:/usr/bin

CMD ["bash", "-l"]