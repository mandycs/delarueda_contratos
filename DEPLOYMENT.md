# Deployment Guide - Contract Signing Service

## Baseline de Base de Datos para Producción ✅

### Estado Actual
- **Baseline Version**: `252808427278_production_baseline_v1_0_0`
- **Fecha de creación**: 2025-08-06
- **Estado**: ✅ Listo para producción

### Para Deployment en Producción (Fresh Database)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno de producción
export DATABASE_URL="postgresql://user:password@localhost/production_db"

# 3. Aplicar migración baseline
alembic upgrade head

# 4. Verificar aplicación correcta
alembic current
# Debería mostrar: 252808427278 (head)

# 5. Crear usuario inicial (opcional)
python create_user.py
```

### Para Ambiente Existente (Desarrollo)

Si ya tienes una base de datos con las migraciones antiguas:

```bash
# El sistema ya está configurado y funcionando
# No necesitas hacer nada adicional
alembic current  # Verificar estado
```

### Estructura del Schema

El baseline incluye las siguientes tablas:

1. **users**: Gestión de usuarios del sistema
   - id (Integer, PK)
   - username, email (únicos)
   - full_name, hashed_password, disabled

2. **contracts**: Gestión de contratos
   - id (Integer, PK)
   - client_name, client_email
   - design_image_path
   - titulo_diseno, puesto_empresa, politica_confirmacion
   - unsigned_pdf_path, signed_pdf_path
   - created_at, signed_at, deleted_at
   - signer_ip, signer_user_agent

3. **default_texts**: Textos predeterminados
   - id (Integer, PK)
   - key (único), content
   - created_at, updated_at

### Migraciones Futuras

Para crear nuevas migraciones:

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar migraciones
alembic upgrade head
```

### Backup de Migraciones Anteriores

Las migraciones fragmentadas anteriores están guardadas en:
`alembic/versions_backup/`

Estas migraciones contenían inconsistencias y han sido consolidadas en el baseline limpio.

---

## Notas de Seguridad

- ✅ Schema limpio sin inconsistencias
- ✅ Baseline consolidado
- ✅ Compatibilidad verificada con modelos actuales
- ✅ Listo para deployment de producción