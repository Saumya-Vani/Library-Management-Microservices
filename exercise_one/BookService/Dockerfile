# Base image
FROM python:3.9-slim

# Creating a working directory /app in the container
WORKDIR /app

# Copying the source code to /app in the container
COPY main.py /app
COPY requirements.txt /app

# Installing the requirements.txt in the container
RUN pip install --no-cache-dir -r requirements.txt

# Making sure that the api runs on port 5002 inside the container
EXPOSE 5006

# Command to run when the container starts
CMD ["python", "main.py"]