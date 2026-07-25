Sure, here's a README documentation for your Dockerized Flask API project. This documentation will guide users through setting up, building, running, and testing the application.

### README.md

```markdown
# Exercise API

This project provides a Flask-based API to search for exercises targeting specific muscle groups. The application is containerized using Docker and Docker Compose for easy deployment and management.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Building the Docker Image](#building-the-docker-image)
- [Running the Docker Container](#running-the-docker-container)
- [Using Docker Compose](#using-docker-compose)
- [Testing the API](#testing-the-api)
- [Endpoints](#endpoints)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup

1. Clone the repository or download the project files to your local machine.
2. Navigate to the project directory.

Ensure your project directory has the following structure:

```
/your-project-directory
  ├── app.py
  ├── exercise.db
  ├── requirements.txt
  ├── Dockerfile
  └── docker-compose.yml
```

## Building the Docker Image

To build the Docker image, run the following command in your project directory:

```bash
docker-compose build
```

## Running the Docker Container

To start the Docker container, run:

```bash
docker-compose up
```

This will start the Flask application inside the Docker container and map the container's port 5000 to your host's port 5200. You can access the API at `http://localhost:5200`.

## Using Docker Compose

The `docker-compose.yml` file is set up to make managing the container easy. You can use the following commands:

- **Build the image**: `docker-compose build`
- **Start the container**: `docker-compose up`
- **Stop the container**: `docker-compose down`
- **View logs**: `docker-compose logs`
- **Run in detached mode**: `docker-compose up -d`

## Testing the API

You can test the API using `curl` or any API client like Postman.

### Example `curl` Commands

#### Query for `Deltoid`:

```bash
curl "http://localhost:5200/search?main_muscle=Deltoid"
```

#### Query for `Biceps Brachii`:

```bash
curl "http://localhost:5200/search?main_muscle=Biceps%20Brachii"
```

### Expected Response

The API will return a JSON array of exercises matching the queried main muscle group.

## Endpoints

### Search Exercises by Main Muscle

- **URL**: `/search`
- **Method**: `GET`
- **Query Parameter**: `main_muscle` (required) - The main muscle group to search for exercises. Supports partial matches.

**Example Request**:

```
GET /search?main_muscle=Deltoid
```

**Response**:

```json
[
    {
        "Exercise_Name": "Overhead Press",
        "Equipment": "Barbell",
        "Variation": "No",
        "Utility": "Basic",
        "Mechanics": "Compound",
        "Force": "Push",
        "Preparation": "Stand with feet shoulder-width apart.",
        "Execution": "Press the barbell overhead until arms are fully extended.",
        "Target_Muscles": "Deltoid",
        "Synergist_Muscles": "Triceps Brachii",
        "Stabilizer_Muscles": "Core",
        "Antagonist_Muscles": "Latissimus Dorsi",
        "Dynamic_Stabilizer_Muscles": "None",
        "Main_muscle": "Deltoid",
        "Difficulty": 3,
        "Secondary_Muscles": "Triceps Brachii",
        "parent_id": null
    }
    ...
]
```

## Troubleshooting

### Common Issues

- **Port Conflict**: Ensure port 5200 is not being used by another application.
- **Database Not Found**: Ensure `exercise.db` is in the project directory.

### Useful Commands

- **Rebuild the Docker Image**:
  ```bash
  docker-compose build
  ```

- **Restart the Docker Container**:
  ```bash
  docker-compose up --force-recreate
  ```

- **Stop and Remove Containers, Networks**:
  ```bash
  docker-compose down
  ```

## License

This project is licensed under the MIT License.
```

### Summary

This README documentation provides clear instructions on how to set up, build, run, and test your Dockerized Flask API project. It also includes a troubleshooting section for common issues and useful Docker commands.