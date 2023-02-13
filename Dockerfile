FROM python:3.9.16

# Install curl
RUN \
    apt update && \
    apt upgrade -y && \
    apt install -y curl && \
    apt install -y vim

# Clone repo
# TODO - pin to commit
RUN \
    git clone https://github.com/uber/piranha.git /piranha

# Install rust \
RUN \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install_rust.sh && \
    sh install_rust.sh -y && \
    . "$HOME/.cargo/env"

# Add .cargo/bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Build latest piranha binary
RUN \
    cd piranha/ && \
    cargo build --release

# Build polyglot-piranha python dep
# RUN \
#     cd piranha/ && \
#     pip install .