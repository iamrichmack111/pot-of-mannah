Certainly! Below is a detailed README file that explains the process of setting up and running a Flask application with Docker. This README covers the creation of the Dockerfile, Docker Compose setup, and running the containerized application.

---

# Pot of Mannah API

## Overview

The Pot of Mannah API is a Flask application that provides endpoints to search food data and retrieve logs. This application is containerized using Docker, allowing for consistent deployment and easy management.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Setup](#setup)
   - [Dockerfile](#dockerfile)
   - [Docker Compose](#docker-compose)
4. [Running the Application](#running-the-application)
5. [Testing the API](#testing-the-api)
6. [Log Management](#log-management)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Ensure you have the following installed:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Project Structure

```
POT-OF-MANNAH-API/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── data/
│       └── food.db
│
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup

### Dockerfile

The `Dockerfile` is used to build the Docker image for the Flask application. It sets up a Python environment, installs dependencies, and specifies how to run the application.

**Dockerfile:**

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Docker Compose

The `docker-compose.yml` file defines and runs multi-container Docker applications. In this setup, it builds the Flask application image and maps ports.

**docker-compose.yml:**

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "5100:5000"
    volumes:
      - ./app/data:/app/data  # Map local data directory to container
    container_name: app-app-1
```

## Running the Application

1. **Build the Docker Image:**

   Build the Docker image using Docker Compose:

   ```bash
   docker-compose build
   ```

2. **Start the Containers:**

   Start the containers and run the Flask application:

   ```bash
   docker-compose up
   ```

   The Flask application will be available at `http://localhost:5100`.

3. **Stopping and Removing Containers:**

   To stop the running containers, use:

   ```bash
   docker-compose down
   ```

## Testing the API

You can test the API endpoints using `curl` or a tool like Postman.

### Search Endpoint

Search for food items by query:

```bash
curl -X GET "http://localhost:5100/search?query=yogurt"
```

### Logs Endpoint

Retrieve logs with optional filters:

```bash
curl -X GET "http://localhost:5100/logs?ip=<IP>&method=<METHOD>&start_date=<START_DATE>&end_date=<END_DATE>"
```

Replace `<IP>`, `<METHOD>`, `<START_DATE>`, and `<END_DATE>` with appropriate values.

## Log Management

Logs are managed using a rotating file handler. Logs are stored in `app.log` within the container and rotated when the file size exceeds 10,000 bytes.

### Accessing Logs

To access logs, you can use:

```bash
docker exec -it app-app-1 sh
cat /app/app.log
```

## Troubleshooting

- **Connection Reset by Peer:** This typically indicates a server issue. Check the Flask logs and ensure the application is correctly configured to listen on `0.0.0.0` and port 5000.
- **ModuleNotFoundError:** Ensure all dependencies are listed in `requirements.txt` and are correctly installed. Verify the Docker build process completes without errors.

### Common Commands

- **View Logs:**

  ```bash
  docker logs app-app-1
  ```

- **Inspect Container:**

  ```bash
  docker exec -it app-app-1 sh
  ```

- **Rebuild and Restart:**

  ```bash
  docker-compose down -v
  docker-compose build
  docker-compose up
  ```

## Conclusion

This setup allows you to easily deploy and manage your Flask application using Docker, with capabilities for rate limiting, logging, and API interaction. For further customization and scaling, refer to Docker and Flask documentation.

