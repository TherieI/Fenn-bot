# Use the official Python image from Docker Hub
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the Python files into the container at /app directory
COPY main.py /app/
COPY requirements.txt /app/

# Copy directories into the container at /app/dir
COPY cogs /app/cogs

# Install any dependencies if needed (e.g., using requirements.txt)
RUN pip install -r requirements.txt

# Command to run the Python script when the container starts
CMD ["python", "main.py"]