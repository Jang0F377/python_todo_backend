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

- `pip install -r requirements.txt`
- Start Postgres in docker: `docker compose up -d --build todo-db`
- You can start the backend locally with the following command:
  `uvicorn src.main:app --reload --env-file .env`
