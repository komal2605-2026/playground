# Use official Python runtime as base image
FROM python:3.14-slim

# Set environment variables
# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app/

# Copy and make entrypoint script executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create user for running app (security best practice)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run entrypoint script
CMD ["/app/entrypoint.sh"]
