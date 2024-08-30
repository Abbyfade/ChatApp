# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Expose the port the app runs on
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]