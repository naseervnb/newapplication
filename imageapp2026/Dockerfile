# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if required (e.g., image processing libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy requirements or project files
COPY . /app

# Install Python dependencies (if you have a requirements.txt, or install directly)
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pillow

# Expose the port your app runs on (update if it uses a specific port like 5000)
EXPOSE 5000

# Command to run your application
CMD ["python", "compress_app.py"]