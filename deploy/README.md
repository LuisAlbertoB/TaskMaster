# Despliegue de TaskMaster API con Docker y Docker Compose

Instrucciones para el despliegue automatizado del servidor backend TaskMaster API en Ubuntu / Debian utilizando Docker, Docker Compose y PostgreSQL.

---

## Estructura del Directorio deploy/

- **Dockerfile**: Imagen de produccion basada en Python 3.12-slim con dependencias de sistema y Gunicorn.
- **docker-compose.yml**: Orquestacion de servicios (PostgreSQL 16 + Django API) con volumenes persistentes para datos de base de datos e imagenes de media.
- **deploy.sh**: Script ejecutable bash para automatizar todo el proceso de instalacion de prerrequisitos, construccion, migraciones y pruebas de salud.

---

## Requisitos Previos

- Servidor Ubuntu 20.04 LTS, 22.04 LTS o Debian 11/12.
- Usuario con privilegios sudo.
- Puertos 8000 (API HTTP) y 5432 (PostgreSQL) disponibles.

---

## Ejecucion del Despliegue Automatizado

Ejecuta el script de despliegue desde la raiz del proyecto o desde el directorio deploy:

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

---

## Flujo del Script deploy.sh

1. Verifica e instala dependencias del sistema (curl, docker, docker-compose-plugin).
2. Asegura que el servicio de Docker este activo.
3. Genera la configuracion db_config/.env para entorno Docker si no existe.
4. Ejecuta docker compose -f deploy/docker-compose.yml up --build -d.
5. Espera a que PostgreSQL este listo e inicia las migraciones y seeders.
6. Establece la contraseña inicial del superusuario a 'Test1234!'.
7. Ejecuta una prueba de salud enviando una peticion cURL de autenticacion a http://localhost:8000/api/token/.

---

## Comandos Utiles de Administracion

### Ver estado de los contenedores
```bash
docker compose -f deploy/docker-compose.yml ps
```

### Ver logs en tiempo real
```bash
docker compose -f deploy/docker-compose.yml logs -f api
```

### Detener los servicios
```bash
docker compose -f deploy/docker-compose.yml down
```

### Reiniciar los servicios manteniendo los datos
```bash
docker compose -f deploy/docker-compose.yml restart
```
