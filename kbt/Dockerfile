# Use a smaller Python base image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY main.py .

# Expose the port the application will run on
EXPOSE 6969

# Command to start the application using gunicorn
CMD ["python", "main.py"]
