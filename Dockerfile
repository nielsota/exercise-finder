FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy all project files needed for install
COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy data files (images, formatted questions, etc.)
COPY data/ ./data/

# Expose port
EXPOSE 8000

# Run the app
CMD ["uv", "run", "uvicorn", "exercise_finder.web.app:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8000"]
