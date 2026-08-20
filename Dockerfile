# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM astral/uv:python3.13-trixie-slim

# Add user that will be used in the container.
RUN useradd wagtail

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl ca-certificates \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Port used by this container to serve HTTP.
EXPOSE 8000

# Create the app directory and a subdirectory for the database. 
RUN mkdir /app
RUN mkdir /app/data
# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy dependency metadata so UV can install the project packages.
COPY pyproject.toml uv.lock /app/

# Create the uv cache directory for the wagtail user and set ownership.
RUN mkdir -p /home/wagtail/.cache/uv && chown -R wagtail:wagtail /home/wagtail
RUN uv sync

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail mhnsite .

# Make entrypoint script executable and set data directory permissions
RUN chmod +x /app/entrypoint.sh && chown wagtail:wagtail /app/data

# Use user "wagtail" to run the build commands below.
USER wagtail

# Collect static files.
RUN uv run python manage.py collectstatic --noinput --clear

# Remove build-time migration
# RUN uv run python manage.py migrate --noinput

# Container starts as root so the entrypoint can fix ownership of the
# (possibly bind-mounted) /app/data directory before dropping to "wagtail".
USER root

ENTRYPOINT ["/app/entrypoint.sh", \
    "uv", "run", "granian", "mhnsite.wsgi:application", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--interface", "wsgi", \
    "--no-ws", \
    "--workers", "3", \
    "--log-level", "info"]