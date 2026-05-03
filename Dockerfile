FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure the session file can be persisted by setting SESSION_NAME to a path
# e.g. set SESSION_NAME=/data/bot_session when running on Fly (mounted volume)

CMD ["python", "run.py"]
