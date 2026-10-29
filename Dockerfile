FROM python:3

ENV TERM=xterm-256color

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  ca-certificates \
  nano \
  vim \
  git \
  && rm -rf /var/lib/apt/lists/*

# Non-root user matching the usual host UID/GID.
RUN groupadd --gid 1000 dev \
  && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash dev

# colored output in bash
RUN echo "PS1='\e[92m\u\e[0m@\e[94m\h\e[0m:\e[35m\w\e[0m# '" >> /home/dev/.bashrc

ENV HOME=/home/dev
ENV PATH="/home/dev/.local/opt/go/bin:/home/dev/.local/bin:/home/dev/go/bin:/home/dev/.bun/bin:${PATH}"

# All user-level tooling is installed as dev so nothing lands in /root.
USER dev

# Install Go using Webi, and fail if the installer fails
RUN set -eu; \
    curl -fsSL --retry 3 --retry-all-errors https://webi.sh/golang -o /tmp/install-go.sh; \
    sh /tmp/install-go.sh; \
    rm /tmp/install-go.sh
RUN go version

# Install boot.dev CLI
RUN go install github.com/bootdotdev/bootdev@latest
RUN bootdev --version

# Mount point for the bootdev config volume
RUN mkdir -p /home/dev/.bootdev && touch /home/dev/.bootdev/config.yaml

# The CLI prefers ~/.bootdev.yaml over the mounted config, so point it at the real one.
# This keeps plain `bootdev` (non-interactive shells, scripts) logged in.
RUN ln -sf /home/dev/.bootdev/config.yaml /home/dev/.bootdev.yaml

# Install opencode
RUN curl -fsSL https://opencode.ai/v2/install -o /tmp/install-opencode.sh \
  && bash /tmp/install-opencode.sh \
  && rm /tmp/install-opencode.sh

# Install uv
RUN curl -fsSL https://astral.sh/uv/install.sh -o /tmp/install-uv.sh \
  && sh /tmp/install-uv.sh \
  && rm /tmp/install-uv.sh

# Install python 3.13
RUN uv python install 3.13

# Install Bun
RUN curl -fsSL https://bun.sh/install -o /tmp/install-bun.sh \
  && bash /tmp/install-bun.sh \
  && rm /tmp/install-bun.sh
RUN bun --version

RUN mkdir -p /home/dev/.local/share/opencode

WORKDIR /workspace

# Run as dev by default, including `docker exec`, which uses the image USER.
USER dev

CMD ["bash"]
