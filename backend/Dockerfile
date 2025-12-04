# Stage 1: Base build stage
FROM python:3.13-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies (disable SSL verification for corporate proxy)
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Install netcat for database health check
USER root
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000 

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Start the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]