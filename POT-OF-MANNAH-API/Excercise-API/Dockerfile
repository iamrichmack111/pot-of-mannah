# Use the official lightweight Python image.
FROM python:3.9-alpine

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt requirements.txt

# Install any dependencies specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container.
COPY . .

# Expose port 5000 for the Flask app.
EXPOSE 5000

# Define the command to run the Flask app with gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]