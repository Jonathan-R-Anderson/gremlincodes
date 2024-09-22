# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies
RUN apk add --no-cache build-base gcc python3-dev libffi-dev openssl-dev curl bash

# Install WebTorrent (Node.js is required)
RUN apk add --no-cache nodejs npm && npm install -g webtorrent-cli

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run Flask using Gunicorn (production-ready WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "9", "--worker-class", "gevent", "app:app"]
