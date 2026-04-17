# ---- Builder Stage ----
# This stage installs build-time dependencies and Python packages.
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies for Pillow/matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpng-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate dependencies
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set a working directory for the build stage
WORKDIR /app

# Copy and install Python dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
# This stage creates the final, clean image for running the application.
FROM python:3.11-slim-bookworm

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code and set ownership
COPY --chown=appuser:appuser . .

# Set the user and activate the virtual environment
USER appuser
ENV PATH="/opt/venv/bin:$PATH"

# Define the command to run the application when the container starts
CMD ["python", "graph.py"]
