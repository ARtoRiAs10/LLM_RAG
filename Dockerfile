FROM python:3.11

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# --- START OF FIX ---
# Add this block to update the OS package list and install the latest
# trusted root certificates. This ensures SSL verification will succeed.
RUN apt-get update && apt-get install -y ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# --- END OF FIX ---

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'src' directory content into the WORKDIR.
COPY ./src .