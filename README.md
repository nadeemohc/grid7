
# Grid7 Django Project

## Overview

Grid7 is a Django-based application designed for managing various features related to Formula 1 products. This README provides instructions for setting up the project on both Linux and Windows environments.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29 or higher)

## Setup Instructions

### 1. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/your-username/grid7.git
cd grid7
```

### 2. Create the `.env` File

Create a `.env` file in the root directory of the project. This file will store environment variables for your application. You can create it with the following command:

```bash
touch .env
```

Add the following environment variables to your `.env` file:

```env
DEBUG=True
SECRET_KEY=your_secret_key_here
DB_NAME=grid7
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432
```

Make sure to replace `your_secret_key_here`, `your_db_user`, and `your_db_password` with actual values.

### 3. Start the Docker Containers

To build and start the Docker containers, run:

```bash
DOCKER_BUILDKIT=1 docker-compose up --build -d
```

### 4. Run Migrations

Once the containers are up, run the following command to apply database migrations:

```bash
docker-compose exec web python manage.py migrate
```

### 5. Create a Superuser (Optional)

To create an admin user for the Django admin panel, run:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to set up your admin user.

### 6. Access the Application

Open your web browser and navigate to `http://localhost:8000/`. You should see the application running.

### 7. Stopping the Containers

To stop the running containers, execute:

```bash
docker-compose down
```

## Troubleshooting

- If you encounter a `ProgrammingError` stating "relation 'django_session' does not exist," ensure you have run the migrations.
- If you see any port conflicts, check if the specified ports (e.g., 5432) are in use and adjust them in the `docker-compose.yml` file.

## Contributing

If you would like to contribute to the project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.