# Use the official Ollama image as the base
FROM ollama/ollama:latest

# This image is also Debian-based.
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*