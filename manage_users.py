#!/usr/bin/env python3
"""
Script completo para gestión de usuarios del sistema
"""
import argparse
import sys
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal
from app.auth import get_password_hash

def list_users(db: Session):
    """Listar todos los usuarios"""
    users = db.query(models.DBUser).all()
    
    if not users:
        print("📋 No hay usuarios registrados en el sistema.")
        return
    
    print(f"📋 Lista de usuarios ({len(users)} total):")
    print("-" * 80)
    print(f"{'ID':<4} {'USERNAME':<20} {'EMAIL':<30} {'FULL NAME':<25}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<4} {user.username:<20} {user.email or 'N/A':<30} {user.full_name or 'N/A':<25}")

def create_user(db: Session, username: str, password: str, email: str = None, full_name: str = None):
    """Crear un nuevo usuario"""
    # Verificar si el usuario ya existe
    db_user = crud.get_user_by_username(db, username=username)
    if db_user:
        print(f"❌ Error: Usuario '{username}' ya existe.")
        return False

    try:
        user_in = schemas.UserCreate(
            username=username,
            password=password,
            email=email,
            full_name=full_name
        )
        
        user = crud.create_user(db=db, user=user_in)
        print(f"✅ Usuario '{user.username}' creado exitosamente.")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email or 'No especificado'}")
        print(f"   - Nombre completo: {user.full_name or 'No especificado'}")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {str(e)}")
        return False

def change_password(db: Session, username: str, password: str, confirm: bool = False):
    """Cambiar contraseña de usuario"""
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        print(f"❌ Error: Usuario '{username}' no encontrado.")
        return False

    print(f"📋 Usuario encontrado:")
    print(f"   - Username: {db_user.username}")
    print(f"   - Email: {db_user.email or 'No especificado'}")
    print(f"   - Nombre completo: {db_user.full_name or 'No especificado'}")

    if not confirm:
        confirm_input = input(f"\n⚠️  ¿Cambiar contraseña de '{username}'? (s/N): ")
        if confirm_input.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada.")
            return False

    try:
        hashed_password = get_password_hash(password)
        db_user.password_hash = hashed_password
        db.commit()
        
        print(f"✅ Contraseña actualizada para '{username}'.")
        return True
        
    except Exception as e:
        print(f"❌ Error al cambiar contraseña: {str(e)}")
        db.rollback()
        return False

def delete_user(db: Session, username: str, confirm: bool = False):
    """Eliminar usuario"""
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        print(f"❌ Error: Usuario '{username}' no encontrado.")
        return False

    print(f"📋 Usuario a eliminar:")
    print(f"   - Username: {db_user.username}")
    print(f"   - Email: {db_user.email or 'No especificado'}")
    print(f"   - ID: {db_user.id}")

    if not confirm:
        confirm_input = input(f"\n⚠️  ¿ELIMINAR permanentemente '{username}'? (s/N): ")
        if confirm_input.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada.")
            return False

    try:
        db.delete(db_user)
        db.commit()
        print(f"✅ Usuario '{username}' eliminado exitosamente.")
        return True
        
    except Exception as e:
        print(f"❌ Error al eliminar usuario: {str(e)}")
        db.rollback()
        return False

def main():
    parser = argparse.ArgumentParser(description="Gestión completa de usuarios del sistema")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando listar
    list_parser = subparsers.add_parser('list', help='Listar todos los usuarios')
    
    # Comando crear
    create_parser = subparsers.add_parser('create', help='Crear nuevo usuario')
    create_parser.add_argument('--username', required=True, help='Nombre de usuario')
    create_parser.add_argument('--password', required=True, help='Contraseña')
    create_parser.add_argument('--email', help='Email del usuario')
    create_parser.add_argument('--full-name', help='Nombre completo')
    
    # Comando cambiar contraseña
    passwd_parser = subparsers.add_parser('passwd', help='Cambiar contraseña')
    passwd_parser.add_argument('--username', required=True, help='Nombre de usuario')
    passwd_parser.add_argument('--password', required=True, help='Nueva contraseña')
    passwd_parser.add_argument('--confirm', action='store_true', help='No preguntar confirmación')
    
    # Comando eliminar
    delete_parser = subparsers.add_parser('delete', help='Eliminar usuario')
    delete_parser.add_argument('--username', required=True, help='Nombre de usuario a eliminar')
    delete_parser.add_argument('--confirm', action='store_true', help='No preguntar confirmación')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return False

    db: Session = SessionLocal()
    success = False
    
    try:
        if args.command == 'list':
            list_users(db)
            success = True
            
        elif args.command == 'create':
            success = create_user(db, args.username, args.password, args.email, args.full_name)
            
        elif args.command == 'passwd':
            success = change_password(db, args.username, args.password, args.confirm)
            
        elif args.command == 'delete':
            success = delete_user(db, args.username, args.confirm)
            
    finally:
        db.close()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)