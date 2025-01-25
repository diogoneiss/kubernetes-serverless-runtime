FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN uv pip install -r requirements.txt --system


# Copy the application into the container.
COPY . /app

# Install the application dependencies.

ENV REDIS_HOST=192.168.121.187

CMD ["python", "app.py"]
