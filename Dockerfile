FROM python:3.10-alpine

RUN apk update
RUN apk upgrade

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

ENV PYTHONUBUFFERED=1

EXPOSE 80

CMD ["python", "Server.py", "go-Server.bat"]


