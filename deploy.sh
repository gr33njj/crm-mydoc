#!/bin/bash
# Скрипт для первоначального деплоя CRM MyDoctor

set -e

echo "🚀 CRM MyDoctor - Deployment Script"
echo "===================================="

# Проверка .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте .env файл на основе .env.example"
    echo "cp .env.example .env"
    exit 1
fi

# Загрузка переменных окружения
source .env

# Проверка обязательных переменных
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your-telegram-bot-token-from-botfather" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN не настроен в .env файле!"
    echo "Получите токен у @BotFather в Telegram"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-in-production-min-32-chars" ]; then
    echo "⚠️  SECRET_KEY не настроен в .env файле!"
    echo "Сгенерируйте случайный ключ длиной минимум 32 символа"
    exit 1
fi

echo "✅ Проверка переменных окружения пройдена"

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p backend/uploads
mkdir -p nginx/ssl
mkdir -p certbot/conf
mkdir -p certbot/www

echo "✅ Директории созданы"

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up -d --build

# Ожидание запуска базы данных
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 10

# Применение миграций БД
echo "🗄️  Инициализация базы данных..."
docker-compose exec -T postgres psql -U mydoc_user -d mydoc_crm < database_schema.sql || true

echo "✅ База данных инициализирована"

# Получение SSL сертификата
echo "🔒 Получение SSL сертификата..."
echo "Внимание: Убедитесь, что DNS записи для $DOMAIN указывают на этот сервер!"
read -p "Продолжить получение SSL сертификата? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose run --rm certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email admin@it-mydoc.ru \
        --agree-tos \
        --no-eff-email \
        -d crm.it-mydoc.ru

    # Перезапуск nginx с SSL
    echo "🔄 Перезапуск Nginx с SSL..."
    docker-compose restart nginx
    
    echo "✅ SSL сертификат установлен"
else
    echo "⚠️  SSL сертификат не установлен. Система будет доступна только по HTTP"
fi

echo ""
echo "✅ Деплой завершён!"
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "📝 Полезные команды:"
echo "  Логи всех сервисов:     docker-compose logs -f"
echo "  Логи backend:           docker-compose logs -f backend"
echo "  Логи frontend:          docker-compose logs -f frontend"
echo "  Логи telegram bot:      docker-compose logs -f telegram_bot"
echo "  Перезапуск:             docker-compose restart"
echo "  Остановка:              docker-compose down"
echo ""
echo "🌐 Приложение доступно по адресу: https://crm.it-mydoc.ru"
echo ""
echo "📱 Telegram Bot:"
echo "  Для привязки аккаунта отправьте боту команду:"
echo "  /start"
echo "  /register your@email.com"
echo ""







