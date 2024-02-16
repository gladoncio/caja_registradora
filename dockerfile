# Use an official Python runtime as a parent image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Copy only the requirements file initially to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN apk add --no-cache build-base libffi-dev openssl-dev mariadb-dev\
    && pip install --no-cache-dir -r /app/requirements.txt

# Instalar Git
RUN apk add --no-cache git

# Configurar Git para ignorar problemas de propiedad en el directorio /app
RUN git config --global --add safe.directory /app

# Expose the port on which your Django app will run
EXPOSE 8000

# Run your Django app
CMD ["python", "app/manage.py", "runserver", "0.0.0.0:8000"]
