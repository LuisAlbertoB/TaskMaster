#!/usr/bin/env bash
set -e

# Directorio del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Funcion auxiliar para ejecutar comandos docker
DOCKER_CMD="docker"
if ! docker info &> /dev/null; then
    if sudo -n docker info &> /dev/null 2>&1; then
        DOCKER_CMD="sudo docker"
    fi
fi

echo "=== INICIANDO DESPLIEGUE AUTOMATIZADO DE TASKMASTER API ==="

# 1. Verificar e instalar requisitos previos
echo "[INFO] Verificando requisitos previos del sistema..."

if ! command -v curl &> /dev/null; then
    echo "[INFO] Instalando curl..."
    sudo apt-get update && sudo apt-get install -y curl
fi

if ! command -v docker &> /dev/null; then
    echo "[INFO] Docker no encontrado. Instalando Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    echo "[SUCCESS] Docker instalado correctamente."
fi

# 2. Verificar servicio Docker activo
if command -v systemctl &> /dev/null; then
    if ! systemctl is-active --quiet docker 2>/dev/null; then
        echo "[INFO] Iniciando servicio Docker..."
        sudo systemctl start docker || true
        sudo systemctl enable docker || true
    fi
fi

# 3. Preparar variables de entorno
ENV_FILE="$PROJECT_DIR/db_config/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "[INFO] Creando archivo db_config/.env por defecto..."
    mkdir -p "$PROJECT_DIR/db_config"
    cat << 'EOF' > "$ENV_FILE"
SECRET_KEY=django-production-key-change-me-to-a-real-secret-2026
DEBUG=False
ALLOWED_HOSTS=*
DB_ENGINE=postgresql
DB_NAME=taskmaster_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
ACCESS_TOKEN_LIFETIME=1800
REFRESH_TOKEN_LIFETIME=604800
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
    echo "[SUCCESS] Archivo .env generado."
fi

# 4. Construir y levantar contenedores con Docker Compose
echo "[INFO] Construyendo y levantando contenedores con Docker Compose..."
cd "$PROJECT_DIR"

if $DOCKER_CMD compose -f deploy/docker-compose.yml up --build -d 2>/dev/null; then
    echo "[SUCCESS] Contenedores iniciados con $DOCKER_CMD compose."
else
    echo "[INFO] Ejecutando con sudo docker compose..."
    sudo docker compose -f deploy/docker-compose.yml up --build -d
fi

# 5. Esperar a que la API este lista
echo "[INFO] Esperando inicio de la API y PostgreSQL..."
MAX_RETRIES=40
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/token/ || true)
    if [ "$HTTP_CODE" = "405" ] || [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ]; then
        echo "[SUCCESS] API respondiendo en http://127.0.0.1:8000/"
        break
    fi
    echo "[INFO] Esperando a la API (Intento $((RETRY_COUNT+1))/$MAX_RETRIES)..."
    sleep 3
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[ERROR] El servicio de API no respondio dentro del tiempo esperado."
    echo "[INFO] Revisa los logs del contenedor con: sudo docker compose -f deploy/docker-compose.yml logs api"
    exit 1
fi

# 6. Prueba de autenticacion automatizada
echo "[INFO] Realizando prueba de autenticacion automatizada (JWT Login)..."
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"name": "superuser", "password": "Test1234!"}' || true)

if echo "$LOGIN_RESPONSE" | grep -q "access"; then
    echo "[SUCCESS] Autenticacion JWT probada exitosamente."
    echo "[INFO] Token obtenido correctamente para usuario superuser."
else
    echo "[WARNING] Respuesta del servidor: $LOGIN_RESPONSE"
fi

echo "=== DESPLIEGUE COMPLETADO EXITOSAMENTE ==="
echo "URL Base de la API: http://127.0.0.1:8000/api/"
echo "Superusuario: superuser / Clave: Test1234!"
