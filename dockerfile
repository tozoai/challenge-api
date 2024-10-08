# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR api

COPY . .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r api/requirements.txt

# Expose port 80
EXPOSE 8080

# Run app.py when the container launches
CMD ["python3", "api/app.py"]