# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Django app code
COPY . /app/

# Collect static files for production (if needed)
RUN python manage.py collectstatic --noinput

# Expose the port that Django runs on
EXPOSE 8000

# Set up gunicorn for production (recommended instead of `runserver`)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "grid_7.wsgi:application"]
