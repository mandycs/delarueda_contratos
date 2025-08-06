# 🚀 Dokploy Deployment Guide

Este proyecto está optimizado para despliegue automático con **Dokploy**.

## 📋 Configuración Rápida para Dokploy

### 1. **Variables de Entorno Requeridas**

En Dokploy, configura estas variables de entorno:

```bash
# Base de datos
POSTGRES_DB=firma_contratos
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=TU_PASSWORD_SEGURO_AQUÍ

# Aplicación
SECRET_KEY=TU_CLAVE_SECRETA_DE_32_CARACTERES_MÍNIMO
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### 2. **Configuración del Proyecto en Dokploy**

1. **Conectar repositorio GitHub** con este proyecto
2. **Dockerfile**: Se usa automáticamente el `Dockerfile` del proyecto
3. **Docker Compose**: Se usa automáticamente el `docker-compose.yml`
4. **Puerto**: `8000` (configurado automáticamente)

### 3. **Servicios Incluidos**

- **🐘 PostgreSQL 17**: Base de datos principal
- **🐍 FastAPI App**: Aplicación principal en puerto 8000
- **📁 Volúmenes persistentes**: Para almacenamiento de archivos

### 4. **Características del Deployment**

✅ **Auto-migraciones**: Se ejecutan automáticamente al iniciar  
✅ **Multi-stage build**: Imagen optimizada y ligera  
✅ **Health checks**: Monitoreo automático de servicios  
✅ **PostgreSQL 17**: Última versión estable  
✅ **Volúmenes persistentes**: Datos seguros entre deployments  
✅ **Usuario no-root**: Seguridad mejorada  

### 5. **Estructura de Archivos**

```
📁 Proyecto/
├── 🐳 Dockerfile                # Imagen de la aplicación
├── 🐳 docker-compose.yml        # Servicios (app + postgres)
├── 📄 requirements.txt          # Dependencias Python
├── 🗄️  alembic/                 # Migraciones de base de datos
├── 📁 app/                      # Código de la aplicación
├── 📁 storage/                  # Archivos persistentes
└── 📋 .env.example              # Plantilla de variables
```

### 6. **Post-Deployment**

Después del primer despliegue:

1. **Verificar servicios**: Ambos contenedores deben estar corriendo
2. **Probar endpoint**: `https://tu-dominio.com/` debe responder
3. **Crear usuario inicial**: Usa el endpoint o herramienta admin

### 7. **Comandos Útiles (Opcional)**

Si necesitas ejecutar comandos dentro del contenedor:

```bash
# Crear usuario administrativo
docker exec -it firma_contratos_app python create_user.py

# Ver logs de la aplicación  
docker logs firma_contratos_app

# Ver logs de la base de datos
docker logs firma_contratos_db
```

### 8. **Backup de Base de Datos**

```bash
# Crear backup
docker exec firma_contratos_db pg_dump -U postgres firma_contratos > backup.sql

# Restaurar backup  
docker exec -i firma_contratos_db psql -U postgres firma_contratos < backup.sql
```

---

## 🔧 Configuración Avanzada (Opcional)

### Variables de Entorno Adicionales

```bash
# Opcional: URL completa de base de datos externa
DATABASE_URL=postgresql://user:pass@external-host:5432/db

# Logs
LOG_LEVEL=info

# Workers de Uvicorn (por defecto: 2)
WORKERS=2
```

---

## ✅ Lista de Verificación Pre-Deploy

- [ ] Variables de entorno configuradas en Dokploy
- [ ] `SECRET_KEY` es seguro (32+ caracteres aleatorios)
- [ ] `POSTGRES_PASSWORD` es seguro
- [ ] Logo de empresa añadido en `storage/logo.png` (opcional)
- [ ] Repositorio GitHub conectado a Dokploy
- [ ] Dominio configurado (si aplica)

---

**¡Listo para deploy! 🚀 Dokploy se encargará del resto automáticamente.**