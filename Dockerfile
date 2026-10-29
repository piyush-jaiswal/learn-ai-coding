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

# Clone
WORKDIR /workspace
RUN git clone https://github.com/bootdotdev/learn-ai-coding-starter.git .
