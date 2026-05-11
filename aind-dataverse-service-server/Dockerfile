FROM python:3.10-slim
WORKDIR /app

# Install git for pip to install from git+ URLs
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Pip install
ADD src ./src
ADD pyproject.toml .
ADD setup.py .

RUN pip install . --no-cache-dir

CMD ["fastapi", "run", "src/aind_dataverse_service_server/main.py", "--port", "80"]
