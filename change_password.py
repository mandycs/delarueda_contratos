#!/usr/bin/env python3
"""
Script para cambiar la contraseña de un usuario
"""
import argparse
from sqlalchemy.orm import Session
from app import crud, models
from app.database import SessionLocal
from app.auth import get_password_hash

def main():
    parser = argparse.ArgumentParser(description="Cambiar la contraseña de un usuario existente.")
    parser.add_argument("--username", required=True, help="Nombre de usuario a actualizar")
    parser.add_argument("--password", required=True, help="Nueva contraseña")
    parser.add_argument("--confirm", action="store_true", 
                       help="Confirmar el cambio sin preguntar")

    args = parser.parse_args()

    db: Session = SessionLocal()
    
    try:
        # Buscar el usuario
        db_user = crud.get_user_by_username(db, username=args.username)
        if not db_user:
            print(f"❌ Error: Usuario '{args.username}' no encontrado.")
            return False

        # Mostrar información del usuario
        print(f"📋 Usuario encontrado:")
        print(f"   - Username: {db_user.username}")
        print(f"   - Email: {db_user.email or 'No especificado'}")
        print(f"   - Nombre completo: {db_user.full_name or 'No especificado'}")
        print(f"   - ID: {db_user.id}")

        # Confirmar el cambio
        if not args.confirm:
            confirm = input(f"\n⚠️  ¿Estás seguro de cambiar la contraseña de '{args.username}'? (s/N): ")
            if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                print("❌ Operación cancelada.")
                return False

        # Hashear la nueva contraseña
        hashed_password = get_password_hash(args.password)
        
        # Actualizar la contraseña en la base de datos
        db_user.password_hash = hashed_password
        db.commit()
        
        print(f"✅ Contraseña actualizada exitosamente para '{args.username}'.")
        print("ℹ️  El usuario puede usar la nueva contraseña inmediatamente.")
        return True
        
    except Exception as e:
        print(f"❌ Error al cambiar la contraseña: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)