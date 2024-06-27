# ToDo Backend

### To run (prerequisite):

Create a root .env file using the .env.example:

```
DB_URL = postgresql+psycopg2://<username>:<password>@<host>/<db>

APP_PORT = 8000

# generate string > `openssl rand -hex 32`
SECRET_KEY = <generated_string>
# HS512 or RS512 or EdDSA
JWT_ALGORITHM = HS256
# Minutes
ACCESS_TOKEN_EXPIRATION = 30

# Using for docker-compose env
DB_PASSWORD = <password>
DB_USER = <user>
DB_DATABASE = <database_name>
DB_PORT = <port>
```

### To run in Docker:

Once your .env file is ready, you should be able to:
`docker compose up -d --build`

### To run locally:

You will have to make these changes to your .env:

```
# In your DB_URL replace <host> with localhost
# Ex.
# Previous
DB_URL = postgresql+psycopg2://root:badPass12345@todo-db/main
# Change to:
DB_URL = postgresql+psycopg2://root:badPass12345@localhost/main
```

> Note: I used pipenv to handle virtual env.

- `pipenv install -r requirements.txt`
- `pipenv shell` - to open a shell in the virtual env.
- Start Postgres in docker:  
  `docker compose up -d --build todo-db`
- You can start the backend locally with the following command:  
  `uvicorn src.main:app --reload --env-file .env`

## Extra stipulations:

### Swagger Page

`http://localhost:8000/docs`

If you happen to be testing the API via an API testing platform such as Postman or Insomnia:

- `/login` endpoint: It takes multipart/form-data with two fields named: `username` and `password`
- any endpoints requiring authentication (listed below) will be expecting a **Bearer Token** auth type.
  - `GET`: `/users/me/`
  - `GET`: `/todos/me/`
  - `POST`: `/todos/`
  - `POST`: `/todos/{todo_id}/completed`
