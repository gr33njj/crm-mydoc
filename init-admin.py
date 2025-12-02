#!/usr/bin/env python3
"""
Скрипт для создания первого администратора
Использование: python init-admin.py
"""

import sys
from getpass import getpass

# Добавляем путь к модулям
sys.path.insert(0, '/app')

from src.database import SessionLocal
from src.models import User, UserRole, Department
from src.auth import get_password_hash


def create_admin():
    """Создание администратора"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже администраторы
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print("⚠️  Администратор уже существует!")
            print(f"Email: {existing_admin.email}")
            overwrite = input("Создать нового администратора? (y/n): ")
            if overwrite.lower() != 'y':
                print("Отменено.")
                return
        
        # Создаём отдел Руководство, если его нет
        dept_management = db.query(Department).filter(Department.name == "Руководство").first()
        if not dept_management:
            dept_management = Department(
                name="Руководство",
                description="Топ-менеджмент"
            )
            db.add(dept_management)
            db.flush()
        
        print("\n🔐 Создание администратора CRM MyDoctor\n")
        
        # Получение данных
        email = input("Email администратора: ").strip()
        if not email or '@' not in email:
            print("❌ Некорректный email!")
            return
        
        # Проверка существующего email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Пользователь с email {email} уже существует!")
            return
        
        full_name = input("Полное имя: ").strip()
        if not full_name:
            print("❌ Имя обязательно!")
            return
        
        password = getpass("Пароль (минимум 6 символов): ")
        if len(password) < 6:
            print("❌ Пароль должен быть минимум 6 символов!")
            return
        
        password_confirm = getpass("Подтвердите пароль: ")
        if password != password_confirm:
            print("❌ Пароли не совпадают!")
            return
        
        phone = input("Телефон (опционально): ").strip() or None
        
        # Создание администратора
        admin = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            phone=phone,
            role=UserRole.ADMIN,
            department_id=dept_management.id,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n✅ Администратор успешно создан!")
        print(f"ID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Имя: {admin.full_name}")
        print(f"Роль: {admin.role.value}")
        print("\n🌐 Войдите в систему: https://crm.it-mydoc.ru/login")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()







