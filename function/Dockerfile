# Use the official Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the function code
COPY . .

# Set environment variables
ENV FUNCTION_TARGET=scrape_lottery
ENV FUNCTION_SOURCE=main.py

# The environment variables will be set by Cloud Functions at runtime
# GCS_BUCKET will be provided by Cloud Build substitutions

# Run the function
CMD ["functions-framework", "--target=scrape_lottery", "--source=main.py"] 