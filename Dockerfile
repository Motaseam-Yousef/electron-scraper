# Use an official Python runtime as a parent image
FROM python:3.9.12-slim-buster

# Set the working directory in the container to /app
WORKDIR /test/doc-py

# Add the current directory contents into the container at /app
ADD . /test/doc-py

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
