# Быстрый старт CRM MyDoctor

## 1. Подготовка сервера (5 минут)

```bash
cd /root/crm-mydoc
chmod +x setup-server.sh
./setup-server.sh
```

**После выполнения перезайдите:**
```bash
logout
ssh root@91.218.112.231
```

## 2. Настройка (2 минуты)

```bash
cd /root/crm-mydoc
cp .env.example .env
nano .env
```

Измените:
- `SECRET_KEY` - случайная строка 32+ символов
- `TELEGRAM_BOT_TOKEN` - токен от @BotFather

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

## 3. Деплой (10 минут)

```bash
chmod +x deploy.sh
./deploy.sh
```

Подтвердите получение SSL сертификата когда спросит.

## 4. Создание администратора (1 минута)

```bash
make admin
```

Или:
```bash
docker-compose exec backend python init-admin.py
```

## 5. Готово! 🎉

**Веб-интерфейс:** https://crm.it-mydoc.ru

**Telegram бот:**
- Найдите бота в Telegram
- `/start`
- `/register your@email.com`

## Полезные команды

```bash
make logs        # Просмотр логов
make restart     # Перезапуск
make backup      # Бэкап БД
make admin       # Создать админа
docker-compose ps # Статус
```

## Если что-то пошло не так

```bash
# Перезапуск всего
docker-compose down
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f telegram_bot

# Проверка
docker-compose ps
```

Подробная документация: `DEPLOYMENT_GUIDE.md`







