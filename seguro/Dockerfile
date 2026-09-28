# syntax=docker/dockerfile:1
FROM python:3.14-slim

# uv: el mismo gestor de dependencias que usa el resto del proyecto.
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /usr/local/bin/uv

WORKDIR /app

# Primero solo las dependencias, para aprovechar la caché de capas de Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Después, el código de la app segura.
COPY seguro/ ./seguro/

# La app NO corre como root: buena práctica también aquí.
RUN useradd --create-home app && chown -R app /app
USER app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "seguro/app.py"]
