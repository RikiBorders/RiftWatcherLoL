FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure Python imports from the `src` folder so Gunicorn can find the package
ENV PYTHONPATH=/app/src

# Serve the Flask app using the application factory `create_app` in the
# existing module `rift_watcher.api.flask`.
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "rift_watcher.api.flask:create_app()"]