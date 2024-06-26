FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD [ "fastapi", "run", "src/main.py", "--port" , "8000"]