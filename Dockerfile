FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system -r requirements.txt

RUN apt update && apt install -y ffmpeg

COPY . .

CMD ["python", "app.py"]