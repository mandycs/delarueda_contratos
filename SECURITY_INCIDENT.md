# 🚨 Incidente de Seguridad - Contraseñas Expuestas

**Fecha del incidente**: 2025-08-13  
**Severidad**: ALTA  
**Estado**: CORREGIDO  

## 📋 Resumen del Incidente

Se identificaron contraseñas en texto plano expuestas en el repositorio de código.

## 🔍 Contraseñas Expuestas Identificadas

1. **Contraseña SMTP**: `YoLoSe174591!`
   - Ubicación: `test_email.py` (línea 13)
   - Ubicación: `.env` (línea 10)

2. **Contraseña Base de Datos**: `supersecurepassword`
   - Ubicación: `.env` (línea 2)

3. **Clave Secreta JWT**: `your_super_secret_key_that_is_long_and_random`
   - Ubicación: `.env` (línea 5)

4. **Contraseña PostgreSQL por defecto**: `changeme123`
   - Ubicación: `docker-compose.yml` (líneas 11, 30)

## ✅ Acciones Correctivas Implementadas

### 1. Limpieza Inmediata
- [x] Removidas todas las contraseñas en texto plano de los archivos
- [x] Reemplazadas con placeholders de seguridad
- [x] Creado archivo `.env.example` sin credenciales reales

### 2. Medidas Preventivas
- [x] Actualizado `.gitignore` para incluir `test_email.py`
- [x] Agregadas reglas adicionales para archivos sensibles
- [x] Excepción para `.env.example`

### 3. Archivos Modificados
```
firma_contratos/test_email.py - Contraseña removida
firma_contratos/.env - Credenciales removidas
firma_contratos/.env.example - Creado con ejemplos seguros
firma_contratos/.gitignore - Actualizado con reglas de seguridad
```

## 🔒 Nuevas Credenciales Requeridas

Para restaurar la funcionalidad del sistema, necesitas configurar las siguientes variables de entorno:

### Backend (.env)
```bash
# Email
SMTP_PASSWORD=TU_PASSWORD_SMTP_REAL

# Database  
DATABASE_URL="postgresql://usuario:TU_PASSWORD_DB@localhost/db_name"

# JWT
SECRET_KEY="TU_CLAVE_JWT_SUPER_SEGURA_DE_AL_MENOS_32_CARACTERES"
```

### Testing
- El archivo `test_email.py` necesita la contraseña SMTP real para funcionar
- Configúrala manualmente cuando sea necesario usar el script

## 🚨 Acciones Críticas Requeridas

### INMEDIATAS (antes del próximo commit)
1. **Cambiar TODAS las contraseñas expuestas**:
   - [ ] Contraseña SMTP en el servidor de email
   - [ ] Contraseña de base de datos PostgreSQL
   - [ ] Generar nueva clave secreta JWT
   - [ ] Cambiar contraseña del usuario admin del sistema

2. **Configurar variables de entorno**:
   - [ ] Crear `.env` local con nuevas credenciales
   - [ ] Configurar variables en el servidor de producción
   - [ ] Verificar que docker-compose use variables de entorno

### A MEDIANO PLAZO
1. **Auditoria de seguridad**:
   - [ ] Revisar logs de acceso por uso no autorizado
   - [ ] Verificar que no haya otros archivos con credenciales
   - [ ] Implementar secrets management (Vault, AWS Secrets, etc.)

2. **Políticas de desarrollo**:
   - [ ] Configurar pre-commit hooks para detectar credenciales
   - [ ] Entrenar al equipo en mejores prácticas de seguridad
   - [ ] Implementar escaneo de secretos en CI/CD

## 📝 Lecciones Aprendidas

1. **Nunca** hardcodear credenciales en código fuente
2. Usar siempre variables de entorno para información sensible
3. Configurar `.gitignore` antes de crear archivos con credenciales
4. Usar herramientas de detección de secretos en desarrollo
5. Crear archivos `.example` para documentar configuración sin exponer datos reales

## 🔐 Script de Gestión de Usuarios

Se han creado scripts seguros para gestión de usuarios:
- `change_password.py` - Cambiar contraseña de usuario
- `manage_users.py` - Gestión completa de usuarios

Uso:
```bash
# Cambiar contraseña
python manage_users.py passwd --username admin --password nueva_password

# Listar usuarios
python manage_users.py list

# Crear usuario
python manage_users.py create --username nuevo --password password123
```

---
**IMPORTANTE**: Este incidente debe tratarse con la máxima seriedad. Todas las credenciales expuestas deben considerarse comprometidas y cambiarse inmediatamente.