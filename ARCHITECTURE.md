# Архитектура CRM MyDoctor

## Технологический стек

### Backend
- **FastAPI** (Python 3.11+) — REST API
- **PostgreSQL 15** — основная БД
- **Redis** — кэш, WebSocket состояния, очереди
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **Celery** — фоновые задачи (отчёты, уведомления)
- **python-telegram-bot** — Telegram интеграция

### Frontend
- **Next.js 14** (App Router) — React framework
- **TypeScript** — типизация
- **TailwindCSS + shadcn/ui** — UI компоненты
- **React Query** — data fetching
- **Zustand** — state management
- **Socket.io Client** — real-time чат
- **PWA** — мобильная версия

### Infrastructure
- **Docker + Docker Compose** — контейнеризация
- **Nginx** — reverse proxy, SSL
- **Certbot** — Let's Encrypt SSL
- **GitHub Actions** — CI/CD (опционально)

## Ключевые сущности системы

### 1. Users (Пользователи)
- id, email, password_hash
- full_name, phone, avatar_url
- telegram_id (для бота)
- role (ADMIN, MANAGER, EMPLOYEE)
- department_id
- is_active, created_at, updated_at

### 2. Departments (Отделы)
- id, name, description
- head_id (руководитель отдела)
- created_at, updated_at

### 3. Tasks (Задачи)
- id, title, description
- creator_id, assignee_id
- department_id
- priority (CRITICAL, IMPORTANT, LOW)
- deadline (nullable, мягкий дедлайн)
- status (NEW, IN_PROGRESS, REVIEW, COMPLETED, CANCELLED)
- parent_task_id (для подзадач)
- completed_at, created_at, updated_at

### 4. TaskComments (Комментарии к задачам)
- id, task_id, user_id
- content, created_at, updated_at

### 5. TaskFiles (Файлы к задачам)
- id, task_id, user_id
- filename, filepath, filesize, mime_type
- created_at

### 6. Checklists (Чек-листы)
- id, task_id
- title, order
- is_completed, completed_at

### 7. ChatRooms (Комнаты чата)
- id, name, type (DIRECT, GROUP, DEPARTMENT)
- department_id (для отдела)
- created_by, created_at

### 8. ChatMembers (Участники чата)
- id, room_id, user_id
- joined_at, last_read_at

### 9. ChatMessages (Сообщения чата)
- id, room_id, sender_id
- content, reply_to_id
- is_edited, created_at, updated_at

### 10. ChatFiles (Файлы в чате)
- id, message_id
- filename, filepath, filesize, mime_type
- created_at

### 11. Reports (Отчёты)
- id, title, period_start, period_end
- generated_by, department_id (nullable)
- content (JSON с данными)
- narrative_text (готовый текстовый отчёт)
- created_at

### 12. Notifications (Уведомления)
- id, user_id, type
- title, content
- is_read, related_task_id, related_chat_id
- created_at

## Основные связи

```
Users (1) ←→ (N) Tasks (creator/assignee)
Users (N) ←→ (1) Departments
Tasks (1) ←→ (N) TaskComments
Tasks (1) ←→ (N) TaskFiles
Tasks (1) ←→ (N) Checklists
Tasks (1) ←→ (N) Tasks (parent-child подзадачи)
ChatRooms (1) ←→ (N) ChatMembers
ChatRooms (1) ←→ (N) ChatMessages
ChatMessages (1) ←→ (N) ChatFiles
Users (1) ←→ (N) Notifications
```

## API Endpoints (основные)

### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Users
- GET /api/users
- GET /api/users/{id}
- PATCH /api/users/{id}
- POST /api/users/{id}/avatar

### Departments
- GET /api/departments
- POST /api/departments
- PATCH /api/departments/{id}

### Tasks
- GET /api/tasks (фильтры: department, assignee, priority, status)
- POST /api/tasks
- GET /api/tasks/{id}
- PATCH /api/tasks/{id}
- DELETE /api/tasks/{id}
- POST /api/tasks/{id}/complete
- POST /api/tasks/{id}/comments
- POST /api/tasks/{id}/files
- GET /api/tasks/{id}/subtasks

### Chat
- GET /api/chat/rooms
- POST /api/chat/rooms
- GET /api/chat/rooms/{id}/messages
- POST /api/chat/rooms/{id}/messages
- POST /api/chat/rooms/{id}/members
- WebSocket: /ws/chat

### Reports
- POST /api/reports/generate
- GET /api/reports
- GET /api/reports/{id}
- GET /api/reports/{id}/download

### Notifications
- GET /api/notifications
- PATCH /api/notifications/{id}/read
- POST /api/notifications/mark-all-read

## Telegram Bot функции

1. **Уведомления:**
   - Новая задача назначена
   - Изменение приоритета задачи
   - Комментарий к вашей задаче
   - Приближение дедлайна
   - Упоминание в чате

2. **Команды:**
   - /start — регистрация Telegram ID
   - /tasks — мои активные задачи
   - /today — задачи на сегодня
   - /complete {task_id} — закрыть задачу
   - /help — справка

## Система отчётов

### Типы отчётов:
1. По выполненным задачам за период
2. По отделу
3. По сотруднику
4. Сводный по всей компании

### Формат narrative-отчёта:
```
ОТЧЁТ О ВЫПОЛНЕННЫХ ЗАДАЧАХ
Период: 01.11.2025 - 30.11.2025
Отдел: Администрация

За отчётный период отделом Администрация было выполнено 47 задач.
Критичных задач выполнено: 5 (10.6%)
Важных задач: 28 (59.6%)
Можно позже: 14 (29.8%)

Среднее время выполнения задачи: 2.3 дня.

Наиболее активные сотрудники:
1. Иванов И.И. - 15 задач
2. Петров П.П. - 12 задач
...
```

## Масштабируемость

1. **Горизонтальное масштабирование:**
   - Несколько инстансов API за load balancer
   - Redis Cluster для распределённого кэша
   - Separate read replicas для PostgreSQL

2. **Вертикальное:**
   - Индексы БД на часто используемых полях
   - Пагинация на всех списковых эндпоинтах
   - Lazy loading в UI

3. **Оптимизации:**
   - CDN для статики
   - Image optimization и compression
   - Database query optimization (N+1 избегание)
   - Rate limiting на API

## Безопасность

- JWT токены (access + refresh)
- Password hashing (bcrypt)
- RBAC (Role-Based Access Control)
- CORS настройка
- Rate limiting
- SQL injection защита (ORM)
- XSS защита
- HTTPS only (SSL)
- Environment variables для секретов







