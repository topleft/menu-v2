# Use Python 3.12 slim image as base
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code
COPY ./src ./src
COPY ./app.py ./app.py

# Development stage
FROM builder as development

# Set environment variables
ENV PYTHONPATH=/app
ENV DYNAMODB_TABLE=recipes
ENV S3_BUCKET=recipe-images

# Expose port for local development
EXPOSE 3000

# Command for development
CMD ["poetry", "run", "sam", "local", "start-api", "--port", "3000", "--env-vars", "env.json"]

# Production stage
FROM builder as production

# Set environment variables
ENV PYTHONPATH=/app

# Create a non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Command for production
CMD ["python", "-m", "app"]
