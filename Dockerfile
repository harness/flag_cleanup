FROM python:3.9.16 as builder

# Install curl
RUN apt update && \
    apt upgrade -y && \
    apt install -y curl && \
    apt install -y vim

RUN git clone https://github.com/uber/piranha.git /piranha

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install_rust.sh && \
    sh install_rust.sh -y && \
    . "$HOME/.cargo/env"

ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install --upgrade pip
RUN pip install polyglot-piranha requests GitPython PyGithub toml

WORKDIR /app
COPY harness_scm.py /app
COPY flag_cleanup.py /app

CMD ["python", "/app/flag_cleanup.py"]