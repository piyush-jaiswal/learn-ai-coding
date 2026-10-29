FROM python:3

# colored output in bash
ENV TERM=xterm-256color
RUN echo "PS1='\e[92m\u\e[0m@\e[94m\h\e[0m:\e[35m\w\e[0m# '" >> /root/.bashrc

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  ca-certificates \
  nano \
  vim \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install Go using Webi, and fail if the installer fails
RUN set -eu; \
    curl -fsSL --retry 3 --retry-all-errors https://webi.sh/golang -o /tmp/install-go.sh; \
    sh /tmp/install-go.sh; \
    rm /tmp/install-go.sh

# Include Webi and Go-installed binary locations
ENV PATH="/root/.local/opt/go/bin:/root/.local/bin:/root/go/bin:${PATH}"
RUN go version

# Install boot.dev CLI
RUN go install github.com/bootdotdev/bootdev@latest
RUN bootdev --version

# Mount point for the bootdev config volume
RUN mkdir -p /root/.bootdev && touch /root/.bootdev/config.yaml

# The CLI prefers ~/.bootdev.yaml over the mounted config, so point it at the real one.
# This keeps plain `bootdev` (non-interactive shells, scripts) logged in.
RUN ln -sf /root/.bootdev/config.yaml /root/.bootdev.yaml

# Install opencode
RUN curl -fsSL https://opencode.ai/v2/install -o /tmp/install-opencode.sh && bash /tmp/install-opencode.sh && rm /tmp/install-opencode.sh

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install python 3.13
RUN uv python install 3.13

# Clone
WORKDIR /workspace
RUN git clone https://github.com/bootdotdev/learn-ai-coding-starter.git .
