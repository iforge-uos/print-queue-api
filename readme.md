  # Print Queue REST API | [![Staging CI/CD](https://github.com/iforge-uos/print-queue-api/actions/workflows/python-package.yml/badge.svg)](https://github.com/iforge-uos/print-queue-api/actions/workflows/python-package.yml)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Arch](https://img.shields.io/badge/Arch%20Linux-1793D1?logo=arch-linux&logoColor=fff&style=for-the-badge)

This is a "simple" application that will provide an endpoint for the print queue program to access and modify the print queue.

**MORE DOCUMENTATION COMING SOON**


## Requirements
- Python >= 3.9
- Postgresql Database
- Redis Database
- Docker (optional)
- Docker Compose (optional)
- This repository
- Google API Credentials (For Google File Uploads)

## Configuration

Configuration is handled via a singular `.env` file that contains the `FLASK_ENV` variable. This is then used to load its respective configuration .env file. So for `FLASK_ENV=development` it will load .env.development. Therefore, you will need at a minimum a `.env.development` and a `.env` file

## Docker
There is an included Docker setup that will build the application and run it as a container with the asynchronous tasks, redis and postgres servers also being spun up as well. To configure the environment for docker copy the `.envexample` file into a `.env.docker` file and change the variable to suit your needs except for the following variables which are required:
- `DB_HOST` = `db`
- `DB_PORT` = `5432`
- `CELERY_BROKER_URL` = `redis://redis:6379/0`
- `CELERY_RESULT_BACKEND` = `redis://redis:6379/0`
- `RATELIMIT_STORAGE_URI` = `redis://redis:6379/1`

To run this docker setup you will need to run the following command:
```bash
docker-compose --env-file .env.docker up --build
```

## Useful Commands
```bash
# Run Application and Celery
flask run

## Run Celery (Windows)
pip install eventlet
celery -A entrypoint_celery worker -l info -P eventlet

## Run Celery (Linux)
celery -A entrypoint_celery  worker -l info

## Build Docker
docker-compose --env-file .env.docker up --build

# Database Commands
flask init-db # Initialize the database
flask drop-db # Drop the database
flask nuke-db # Drop the database and reinitialize it
flask seed-db # Seed the database with test data
flask seed-default-printers # Seed the database with the default printers
flask seed-default-authorisation # Seed the database with the default authorisation permissions and roles
flask restore-db # Restore the database from backup.dump
flask backup-db # Backup the database to backup.dump

# Application Specific Commands
flask clear-all-blacklist # Clear all blacklisted tokens from the database (useful for testing)
flask clear-expired-blacklist # Clear all expired blacklisted tokens from the database (useful for general maintennance)
flask app-status # Check the status of the application
flask list-routes # List all the routes in the application
```

## Endpoints
```
auth.login                                      OPTIONS,POST            /api/v1/auth/login
auth.logout                                     DELETE,OPTIONS          /api/v1/auth/logout
auth.refresh                                    OPTIONS,POST            /api/v1/auth/refresh
bootstrap.static                                GET,HEAD,OPTIONS        /static/bootstrap/<path:filename>
file_upload.upload_gcode                        OPTIONS,POST            /api/v1/file_upload/upload_gcode
file_upload.upload_stl                          OPTIONS,POST            /api/v1/file_upload/upload_stl
maintenance logs.create                         OPTIONS,POST            /api/v1/maintenance/add
maintenance logs.delete_by_id                   DELETE,OPTIONS          /api/v1/maintenance/delete/<int:log_id>
maintenance logs.update_by_id                   OPTIONS,PUT             /api/v1/maintenance/update/<int:log_id>
maintenance logs.view_all_by_printer_id         GET,HEAD,OPTIONS        /api/v1/maintenance/view/all/<int:printer_id>
maintenance logs.view_all_by_printer_name       GET,HEAD,OPTIONS        /api/v1/maintenance/view/all/<string:printer_name>
maintenance logs.view_single_by_id              GET,HEAD,OPTIONS        /api/v1/maintenance/view/single/<int:log_id>
misc.test                                       GET,HEAD,OPTIONS        /api/v1/misc/toast
misc.test_2                                     GET,HEAD,OPTIONS        /api/v1/misc/legal
misc.test_celery                                GET,HEAD,OPTIONS        /api/v1/misc/test_celery
print jobs.accept_approval_job                  OPTIONS,PUT             /api/v1/jobs/approve/accept/<int:job_id>
print jobs.complete_job                         OPTIONS,PUT             /api/v1/jobs/complete/<int:job_id>
print jobs.create                               OPTIONS,POST            /api/v1/jobs/add
print jobs.delete_job                           DELETE,OPTIONS          /api/v1/jobs/delete/<int:job_id>
print jobs.fail_job                             OPTIONS,PUT             /api/v1/jobs/fail/<int:job_id>
print jobs.queue_job                            OPTIONS,PUT             /api/v1/jobs/queue/<int:job_id>
print jobs.reject_approval_job                  OPTIONS,PUT             /api/v1/jobs/approve/reject/<int:job_id>
print jobs.reject_job                           OPTIONS,PUT             /api/v1/jobs/reject/<int:job_id>
print jobs.review_job                           OPTIONS,PUT             /api/v1/jobs/review/<int:job_id>
print jobs.start_queued_job                     OPTIONS,PUT             /api/v1/jobs/start/<int:job_id>
print jobs.view_job_single                      GET,HEAD,OPTIONS        /api/v1/jobs/view/<int:job_id>
print jobs.view_jobs_by_status                  GET,HEAD,OPTIONS        /api/v1/jobs/view/<string:status>
printers.create                                 OPTIONS,POST            /api/v1/printers/add
printers.delete_by_id                           DELETE,OPTIONS          /api/v1/printers/delete/<int:printer_id>
printers.delete_by_name                         DELETE,OPTIONS          /api/v1/printers/delete/<string:printer_name>
printers.increment_by_id                        OPTIONS,PUT             /api/v1/printers/increment/<int:printer_id>
printers.increment_by_name                      OPTIONS,PUT             /api/v1/printers/increment/<string:printer_name>
printers.update_by_id                           OPTIONS,PUT             /api/v1/printers/update/<int:printer_id>
printers.update_by_name                         OPTIONS,PUT             /api/v1/printers/update/<string:printer_name>
printers.view_all_printers                      GET,HEAD,OPTIONS        /api/v1/printers/view/all/
printers.view_by_id                             GET,HEAD,OPTIONS        /api/v1/printers/view/<int:printer_id>
printers.view_by_name                           GET,HEAD,OPTIONS        /api/v1/printers/view/<string:printer_name>
static                                          GET,HEAD,OPTIONS        /static/<path:filename>
users.create                                    OPTIONS,POST            /api/v1/users/add
users.delete_by_email                           DELETE,OPTIONS          /api/v1/users/delete/<string:user_email>
users.delete_by_id                              DELETE,OPTIONS          /api/v1/users/delete/<int:user_id>
users.update_by_email                           OPTIONS,PUT             /api/v1/users/update/<string:user_email>
users.update_by_id                              OPTIONS,PUT             /api/v1/users/update/<int:user_id>
users.view_all_users                            GET,HEAD,OPTIONS        /api/v1/users/view/all
users.view_by_email                             GET,HEAD,OPTIONS        /api/v1/users/view/<string:user_email>
users.view_by_id                                GET,HEAD,OPTIONS        /api/v1/users/view/<int:user_id>
```