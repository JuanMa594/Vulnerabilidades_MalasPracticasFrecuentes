---
paths:
  - "**/Dockerfile"
  - "compose.yml"
  - "compose.*.yml"
---

# Docker

Nada sale de esta máquina: ver "Solo local, sin excepciones" en CLAUDE.md.

- Puertos publicados solo en localhost: `"127.0.0.1:8001:8000"`, nunca `"8001:8000"` ni `"0.0.0.0:8001:8000"`.
- Dentro del contenedor la app sí escucha en `0.0.0.0`: esa es la red interna de Docker. Lo que se limita es la publicación en el host.
- Postgres no publica puertos: pgAdmin y las apps llegan a él por la red de Docker.
- Prohibido `network_mode: host`.
- Imágenes con versión fija (por ejemplo `postgres:18`, `python:3.14-slim`), nunca `latest`.
- Credenciales desde `.env` (`${POSTGRES_PASSWORD}`); `.env.example` documenta cada variable.
- Las apps no corren como root dentro del contenedor, tampoco la insegura: así el daño de las demos queda contenido.
