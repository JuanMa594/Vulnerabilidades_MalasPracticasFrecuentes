---
paths:
  - "**/Dockerfile"
  - "compose.yml"
  - "compose.*.yml"
---

# Docker

- Puertos publicados solo en localhost: `"127.0.0.1:8001:8000"`, nunca `"8001:8000"`.
- Imágenes con versión fija (por ejemplo `postgres:18`, `python:3.14-slim`), nunca `latest`.
- Credenciales desde `.env` (`${POSTGRES_PASSWORD}`); `.env.example` documenta cada variable.
- Las apps no corren como root dentro del contenedor, tampoco la insegura: así el daño de las demos queda contenido.
