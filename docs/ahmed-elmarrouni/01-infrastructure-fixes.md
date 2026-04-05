# Infrastructure and Docker Fixes

I made a few updates to the local Docker setup to make it more stable and fix some startup errors. Here is a summary of what I did:

## 1. Automated MLflow Database Creation

**What I changed:** I created a new folder called `postgres-init/` with an `init-mlflow.sql` file inside it. Then, I mounted it to the PostgreSQL container in the `docker-compose.yml` file.

**Why I did this:** Before, the `mlflow` container kept crashing because the `mlflow` database didn't exist yet. PostgreSQL automatically runs any `.sql` scripts placed in its startup folder. With this change, the database is created automatically, so developers don't have to type manual SQL commands to make MLflow work.

## 2. Fixed MLflow Server Command

**What I changed:** I changed the multiline command (`command: >`) in the `mlflow` service to one single line using `bash -c`. I also corrected the exposed port to `5000`.

**Why I did this:** The YAML multiline format was causing Docker to ignore the `--host 0.0.0.0` part of the command. Because of this, MLflow was starting on `127.0.0.1` inside the container, which made it impossible to open the MLflow UI in the browser. Putting everything on one line fixes this and makes sure the server gets all the right commands.

## 3. Prevented Local Port Conflicts (Just for my setup)

**What I changed:** I updated the external ports for PostgreSQL (to `5433:5432`) && Redis (to `6380:6379`) in the `docker-compose.yml` file.

**Why I did this:** I already have PostgreSQL and Redis running on my computer for other things. Changing these ports stopped the "address already in use" error for me.

_(Note: This change was just to help my local environment run smoothly. You can ignore this part in the PR review, or let me know if you want me to change the ports back to the original ones!)_
