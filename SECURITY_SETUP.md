# 🔒 Configuración de Seguridad - Sistema de Contratos

## 📋 Configuración Inicial de Seguridad

### 1. Variables de Entorno Requeridas

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Configura las siguientes variables críticas:

```env
# JWT - Generar clave de 32+ caracteres
SECRET_KEY="tu_clave_jwt_super_segura_aqui"

# Email SMTP
SMTP_PASSWORD=tu_password_smtp_real

# Base de datos
DATABASE_URL="postgresql://usuario:password_seguro@localhost/db_name"
```

### 2. Generar Credenciales Seguras

```bash
# Generar JWT Secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generar password seguro
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%'; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

### 3. Gestión de Usuarios

```bash
# Listar usuarios
python manage_users.py list

# Cambiar contraseña
python manage_users.py passwd --username admin --password nueva_password

# Crear usuario
python manage_users.py create --username nuevo --password password123 --email user@example.com
```

## 🚨 Checklist de Seguridad

### Antes de Despliegue
- [ ] Todas las contraseñas por defecto han sido cambiadas
- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Variables de entorno configuradas en producción
- [ ] Credenciales de base de datos son únicas y seguras
- [ ] Contraseña SMTP es la correcta y actual

### Después de Despliegue
- [ ] Login funciona correctamente
- [ ] Envío de emails funciona
- [ ] Base de datos conecta correctamente
- [ ] Logs no muestran credenciales en texto plano

### Mantenimiento Regular
- [ ] Rotar credenciales cada 90 días
- [ ] Revisar logs por actividad sospechosa
- [ ] Mantener scripts de gestión de usuarios actualizados
- [ ] Verificar que .gitignore previene exposición de credenciales

## 🔐 Rotación de Credenciales

### JWT Secret
```bash
# 1. Generar nueva clave
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. Actualizar .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=\"$NEW_SECRET\"/" .env

# 3. Reiniciar aplicación
docker compose restart app
```

### Contraseñas de Usuario
```bash
# Cambiar contraseña admin
python manage_users.py passwd --username admin --password nueva_password_segura
```

## 📞 En Caso de Incidente de Seguridad

1. **Inmediatamente**:
   - Cambiar todas las credenciales expuestas
   - Revisar logs de acceso
   - Notificar al equipo de desarrollo

2. **Investigación**:
   - Identificar alcance de la exposición
   - Verificar si hubo acceso no autorizado
   - Documentar el incidente

3. **Remedición**:
   - Implementar medidas correctivas
   - Actualizar procedimientos de seguridad
   - Revisar y mejorar controles existentes

## 🛡️ Mejores Prácticas

- **Nunca** hardcodear credenciales en código
- Usar variables de entorno para toda información sensible
- Rotar credenciales regularmente
- Mantener `.gitignore` actualizado
- Usar herramientas de detección de secretos
- Implementar logging seguro (sin credenciales)
- Revisar código antes de commits para credenciales expuestas