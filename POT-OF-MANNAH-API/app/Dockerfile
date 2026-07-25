# Use an official Python runtime based on Alpine Linux
FROM python:3.11-alpine

# Set environment variables to ensure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install SQLite and other dependencies
RUN apk update && \
    apk add --no-cache sqlite sqlite-libs gcc musl-dev libffi-dev

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app/

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define the command to run the Flask application using Python
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
