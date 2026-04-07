# CRM MyDoctor

Внутренняя система управления задачами, коммуникациями и отчётами для частной медицинской сети.

## Возможности

- ✅ Управление задачами с приоритетами и мягкими дедлайнами
- 👥 Пользователи, роли и отделы
- 💬 Встроенный корпоративный чат с real-time
- 📊 Генерация текстовых отчётов в narrative-стиле
- 🤖 Telegram-бот для уведомлений и быстрых команд
- 📱 Mobile-first PWA дизайн
- 🔐 Аутентификация и авторизация на основе ролей

## Технологический стек

### Backend
- FastAPI (Python 3.11)
- PostgreSQL 15
- Redis
- SQLAlchemy + Alembic
- Celery
- python-telegram-bot

### Frontend
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- React Query
- Socket.io
- PWA

### Infrastructure
- Docker & Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt SSL

## Быстрый старт

### 1. Подготовка сервера

```bash
# Подключитесь к серверу
ssh root@91.218.112.231

# Клонируйте или загрузите проект
cd /root/crm-mydoc

# Запустите скрипт подготовки сервера
chmod +x setup-server.sh
./setup-server.sh

# Перезайдите в систему
logout
```

### 2. Настройка окружения

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env и заполните:
# - SECRET_KEY (случайная строка минимум 32 символа)
# - TELEGRAM_BOT_TOKEN (от @BotFather)
nano .env
```

### 3. Деплой приложения

```bash
# Запустите скрипт деплоя
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- Проверит конфигурацию
- Создаст необходимые директории
- Соберёт и запустит Docker контейнеры
- Инициализирует базу данных
- Получит SSL сертификат от Let's Encrypt

### 4. Создание администратора

```bash
# Подключитесь к контейнеру backend
docker-compose exec backend bash

# Создайте первого администратора через Python
python -c "
from src.database import SessionLocal
from src.models import User, UserRole
from src.auth import get_password_hash

db = SessionLocal()

admin = User(
    email='admin@it-mydoc.ru',
    password_hash=get_password_hash('admin123'),
    full_name='Администратор',
    role=UserRole.ADMIN,
    is_active=True
)

db.add(admin)
db.commit()
print('Администратор создан!')
"
```

## Использование

### Веб-интерфейс

Откройте в браузере: https://crm.it-mydoc.ru

Войдите с учётными данными администратора.

### Telegram Bot

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Привяжите аккаунт: `/register your@email.com`
4. Используйте команды:
   - `/tasks` - Мои активные задачи
   - `/today` - Задачи на сегодня
   - `/complete <ID>` - Закрыть задачу
   - `/help` - Справка

## Управление системой

### Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Логи отдельного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f telegram_bot

# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Обновление (после изменений)
docker-compose up -d --build

# Бэкап базы данных
docker-compose exec postgres pg_dump -U mydoc_user mydoc_crm > backup_$(date +%Y%m%d).sql

# Восстановление базы данных
docker-compose exec -T postgres psql -U mydoc_user mydoc_crm < backup.sql
```

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Системные ресурсы
htop
```

## Структура проекта

```
crm-mydoc/
├── backend/                # Backend API (FastAPI)
│   ├── src/
│   │   ├── routers/       # API endpoints
│   │   ├── models.py      # SQLAlchemy модели
│   │   ├── schemas.py     # Pydantic схемы
│   │   ├── auth.py        # Аутентификация
│   │   ├── main.py        # FastAPI приложение
│   │   └── telegram_bot.py # Telegram бот
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # Frontend (Next.js)
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React компоненты
│   │   ├── lib/          # API клиент
│   │   └── store/        # Zustand store
│   ├── package.json
│   └── Dockerfile
├── nginx/                 # Nginx конфигурация
│   └── nginx.conf
├── database_schema.sql    # SQL схема БД
├── docker-compose.yml     # Docker Compose
├── deploy.sh             # Скрипт деплоя
├── setup-server.sh       # Скрипт подготовки сервера
├── .env.example          # Пример переменных окружения
└── README.md
```

## Основные сущности

- **Users** - Пользователи с ролями (ADMIN, MANAGER, EMPLOYEE)
- **Departments** - Отделы организации
- **Tasks** - Задачи с приоритетами и статусами
- **ChatRooms** - Комнаты чата (личные, групповые, отделов)
- **ChatMessages** - Сообщения в чате
- **Reports** - Сгенерированные отчёты
- **Notifications** - Уведомления пользователей

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущий пользователь

### Задачи
- `GET /api/tasks` - Список задач
- `POST /api/tasks` - Создать задачу
- `GET /api/tasks/{id}` - Получить задачу
- `PATCH /api/tasks/{id}` - Обновить задачу
- `POST /api/tasks/{id}/complete` - Завершить задачу
- `POST /api/tasks/{id}/comments` - Добавить комментарий

### Чат
- `GET /api/chat/rooms` - Комнаты чата
- `GET /api/chat/rooms/{id}/messages` - Сообщения
- `POST /api/chat/rooms/{id}/messages` - Отправить сообщение

### Отчёты
- `POST /api/reports` - Сгенерировать отчёт
- `GET /api/reports` - Список отчётов
- `GET /api/reports/{id}` - Получить отчёт
- `GET /api/reports/{id}/download` - Скачать отчёт

## Масштабирование

Система готова к горизонтальному масштабированию:

1. Несколько инстансов backend за load balancer
2. Redis Cluster для распределённого кэша
3. PostgreSQL read replicas
4. CDN для статических файлов

## Безопасность

- JWT токены для аутентификации
- HTTPS only (SSL от Let's Encrypt)
- Password hashing (bcrypt)
- RBAC (Role-Based Access Control)
- Rate limiting на API
- Firewall (UFW)
- Fail2ban защита от брутфорса

## Поддержка

Для вопросов и поддержки:
- Email: admin@it-mydoc.ru
- Telegram: @gr33njj

## Лицензия

Проприетарное ПО для MyDoctor







