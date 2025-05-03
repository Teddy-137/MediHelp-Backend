# Use official Python base image (use a specific version to avoid network issues)
FROM python:3.11-slim

# Install system dependencies for Django and Spatialite
RUN apt-get update && apt-get install -y \
    libsqlite3-mod-spatialite \
    spatialite-bin \
    binutils \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media
RUN chmod -R 755 /app/staticfiles /app/media

# Skip collectstatic during build (will be run in the entrypoint)
ENV DJANGO_SKIP_COLLECTSTATIC=1

# Expose the port
EXPOSE 8000

# Copy and set permissions for entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "medihelp.wsgi:application"]