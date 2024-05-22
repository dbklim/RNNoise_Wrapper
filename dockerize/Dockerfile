# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variable
ENV APP_PORT="5000"

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update the package list and install ffmpeg
RUN apt-get update && \
apt-get install -y ffmpeg && \
rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/dockerize/requirements.txt

# Make port 1555 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "-m", "dockerize.app"]
# CMD ["python"]