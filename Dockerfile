FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

RUN apt update && apt install -y ffmpeg

COPY . .

CMD ["tail", "-f", "/dev/null"]