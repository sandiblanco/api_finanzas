#!/bin/bash
# Script de Deployment Automático para Azure
# Finance API - Proyecto Diseño de Software TEC
set -e  # Detener si hay algún error

echo "==============================================================="
echo "                  Deployment Automático a Azure               "
echo "                  Finance API - TEC San Carlos               "
echo "==============================================================="
echo ""

# Configuración
read -p "Ingresa tu nombre de usuario (sin espacios, ej: jperez): " USERNAME
APP_NAME="finance-api-${USERNAME}"
RESOURCE_GROUP="finance-api-rg"
LOCATION="centralus"
PLAN_NAME="finance-api-plan"

echo ""
echo "Configuración:"
echo "   - Nombre de la app: ${APP_NAME}"
echo "   - Grupo de recursos: ${RESOURCE_GROUP}"
echo "   - Ubicación: ${LOCATION}"
echo "   - Plan: F1 (Gratis)"
echo ""

read -p "¿Continuar con el deployment? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo "Deployment cancelado"
    exit 1
fi

echo ""
echo "Generando clave secreta segura..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "Paso 1/5: Creando grupo de recursos..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "Paso 2/5: Creando App Service Plan (F1 - Gratis)..."
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku F1 \
  --is-linux

echo "Paso 3/5: Creando Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON:3.11"

echo "Paso 4/5: Configurando variables de entorno..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    SECRET_KEY="$SECRET_KEY" \
    DATA_DIR="/tmp/finance_data" \
    DEBUG="False" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="30" \
    API_VERSION="v1" \
    PROJECT_NAME="Personal Finance API" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo "Configurando startup command..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --access-logfile - --error-logfile - --worker-class uvicorn.workers.UvicornWorker src.main:app"

echo "Paso 5/5: Configurando deployment desde GitHub..."
read -p "Ingresa tu usuario de GitHub: " GITHUB_USER
read -p "Ingresa el nombre del repositorio: " GITHUB_REPO
read -p "Ingresa la rama (master/main) [master]: " GITHUB_BRANCH
GITHUB_BRANCH=${GITHUB_BRANCH:-master}

echo ""
echo "Conectando con GitHub..."
echo "   Repo: https://github.com/${GITHUB_USER}/${GITHUB_REPO}"
echo "   Rama: ${GITHUB_BRANCH}"
echo ""

az webapp deployment source config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url "https://github.com/${GITHUB_USER}/${GITHUB_REPO}" \
  --branch $GITHUB_BRANCH \
  --manual-integration

echo ""
echo "==============================================================="
echo "                Deployment Completado                        "
echo "==============================================================="
echo ""
echo "URLs de tu API:"
echo "   API:     https://${APP_NAME}.azurewebsites.net"
echo "   Swagger: https://${APP_NAME}.azurewebsites.net/docs"
echo "   Health:  https://${APP_NAME}.azurewebsites.net/health"
echo ""
echo "El deployment puede tardar 5-10 minutos."
echo ""
echo "Comandos útiles:"
echo "   Ver logs:      az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME"
echo "   Reiniciar app: az webapp restart -g $RESOURCE_GROUP -n $APP_NAME"
echo "   Ver estado:    az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query state"
echo ""
echo "IMPORTANTE: Guarda estas URLs para la entrega del proyecto"
echo ""
echo "SECRET_KEY generado: $SECRET_KEY"
echo "(Guarda esto en un lugar seguro)"
echo ""