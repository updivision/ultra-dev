FROM python:3.11-slim

# Install GitHub CLI
RUN apt-get update && \
    apt-get install -y curl unzip ca-certificates gnupg && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
      https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# copy your entrypoint into a known, immutable location
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# now switch to /action for the rest of your code
WORKDIR /action
COPY requirements.txt ./
COPY src/ ./src/
RUN pip install --no-cache-dir -r requirements.txt

# use the absolute path so Docker will find it, even though the runner
# mounts the workspace (and forces workdir) to /github/workspace
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
