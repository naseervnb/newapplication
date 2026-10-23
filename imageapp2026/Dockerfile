# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for tkinter
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    tcl

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir pillow

# Expose the port your app runs on
EXPOSE 5000

# Command to run your application
CMD ["python", "compress_app.py"]