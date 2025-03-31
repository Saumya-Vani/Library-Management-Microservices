FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port (if needed, for monitoring or REST APIs in the future)
EXPOSE 5003

# Command to start the consumer
CMD ["python", "main.py"]
 
