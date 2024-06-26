# syntax=docker/dockerfile:1.3-labs

ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango1.0-dev \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create Fontconfig cache directory and set permissions
RUN mkdir -p /var/cache/fontconfig && \
    chmod 777 /var/cache/fontconfig

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN mkdir -p /app/logs /app/staticfiles && touch /app/logs/django_debug.log && \
    chown -R appuser:appuser /app/logs /app/staticfiles && chmod 755 /app/logs /app/staticfiles && \
    chmod 644 /app/logs/django_debug.log

# Copy requirements.txt before installing dependencies
COPY requirements.txt .

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN --mount=type=cache,id=s/6a6cf542-1b62-478e-96e7-cfbe9a4a4038-/pip-cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt


# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .


RUN python manage.py collectstatic --noinput


# Expose the port that the application listens on.
EXPOSE $PORT

# Run the application.
CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL || true && python manage.py runserver 0.0.0.0:$PORT"]
