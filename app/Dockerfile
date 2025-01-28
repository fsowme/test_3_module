FROM python:3.11

WORKDIR /app
RUN mkdir persist

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY ./src /app

CMD ["uvicorn", "main:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
