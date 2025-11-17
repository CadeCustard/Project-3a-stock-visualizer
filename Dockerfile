# Use an official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port Flask runs on
EXPOSE 5000

# Command to run your flask app
CMD ["python", "app.py"]
