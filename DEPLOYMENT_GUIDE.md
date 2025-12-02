# Руководство по деплою CRM MyDoctor

## Предварительные требования

- Сервер Ubuntu 20.04/22.04
- Минимум 2 CPU, 4GB RAM, 20GB SSD
- Доменное имя с настроенными DNS записями
- Root доступ к серверу

## Пошаговая инструкция

### Шаг 1: DNS настройка

Добавьте A-запись для вашего домена:

```
Тип: A
Имя: crm.it-mydoc.ru
Значение: 91.218.112.231
TTL: 3600
```

Проверьте DNS:
```bash
nslookup crm.it-mydoc.ru
```

### Шаг 2: Подключение к серверу

```bash
ssh root@91.218.112.231
```

### Шаг 3: Подготовка сервера

```bash
cd /root/crm-mydoc
chmod +x setup-server.sh
./setup-server.sh
```

Этот скрипт:
- Обновит систему
- Установит Docker и Docker Compose
- Настроит firewall (UFW)
- Установит fail2ban
- Оптимизирует системные параметры
- Создаст swap-файл

**ВАЖНО:** После выполнения перезайдите в систему:
```bash
logout
ssh root@91.218.112.231
```

### Шаг 4: Получение Telegram Bot Token

1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте `/newbot`
4. Следуйте инструкциям
5. Скопируйте полученный токен

### Шаг 5: Настройка окружения

```bash
cd /root/crm-mydoc

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env
nano .env
```

Заполните обязательные параметры:

```env
# Сгенерируйте случайный ключ минимум 32 символа
SECRET_KEY=your-super-secret-random-key-min-32-chars

# Токен от BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 6: Деплой приложения

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт выполнит:
1. Проверку конфигурации
2. Создание директорий
3. Сборку и запуск Docker контейнеров
4. Инициализацию базы данных
5. Получение SSL сертификата (при подтверждении)

### Шаг 7: Создание администратора

```bash
# Используя Makefile
make admin

# Или напрямую
docker-compose exec backend python init-admin.py
```

Введите:
- Email: admin@it-mydoc.ru
- Имя: Администратор
- Пароль: (минимум 6 символов)
- Телефон: (опционально)

### Шаг 8: Проверка работы

1. **Веб-интерфейс:**
   - Откройте https://crm.it-mydoc.ru
   - Войдите с учётными данными администратора

2. **Telegram Bot:**
   - Найдите вашего бота в Telegram
   - Отправьте `/start`
   - Привяжите аккаунт: `/register admin@it-mydoc.ru`

3. **Проверка сервисов:**
```bash
docker-compose ps
```

Все сервисы должны быть в статусе "Up".

## Управление системой

### Просмотр логов

```bash
# Все сервисы
make logs

# Отдельные сервисы
make logs-backend
make logs-frontend
make logs-bot
make logs-nginx

# Или напрямую
docker-compose logs -f backend
```

### Перезапуск

```bash
# Все сервисы
make restart

# Отдельный сервис
docker-compose restart backend
```

### Обновление кода

```bash
# После изменений в коде
make build

# Или
docker-compose up -d --build
```

### Бэкап базы данных

```bash
# Создать бэкап
make backup

# Бэкап сохранится в backups/backup_YYYYMMDD_HHMMSS.sql
```

### Восстановление БД

```bash
make restore
# Выберите файл бэкапа из списка
```

## Мониторинг

### Статус контейнеров

```bash
docker-compose ps
```

### Использование ресурсов

```bash
docker stats
```

### Системные ресурсы

```bash
htop
free -h
df -h
```

### Логи Nginx

```bash
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

## Решение проблем

### SSL сертификат не получен

```bash
# Проверьте DNS
nslookup crm.it-mydoc.ru

# Убедитесь, что порты открыты
sudo ufw status

# Попробуйте получить сертификат вручную
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@it-mydoc.ru \
  --agree-tos \
  --no-eff-email \
  -d crm.it-mydoc.ru
```

### База данных не запускается

```bash
# Проверьте логи
docker-compose logs postgres

# Пересоздайте volume
docker-compose down
docker volume rm crm-mydoc_postgres_data
docker-compose up -d
```

### Backend ошибки

```bash
# Логи
docker-compose logs backend

# Перезапуск
docker-compose restart backend

# Проверка переменных окружения
docker-compose exec backend env | grep DATABASE_URL
```

### Telegram бот не отвечает

```bash
# Проверьте логи
docker-compose logs telegram_bot

# Проверьте токен
docker-compose exec telegram_bot env | grep TELEGRAM

# Перезапуск
docker-compose restart telegram_bot
```

## Производительность

### Увеличение лимитов PostgreSQL

Отредактируйте `docker-compose.yml`:

```yaml
postgres:
  command: postgres -c shared_buffers=256MB -c max_connections=200
```

### Масштабирование Backend

```bash
# Запустить несколько инстансов
docker-compose up -d --scale backend=3
```

Настройте load balancer в nginx.

## Безопасность

### Регулярные обновления

```bash
# Система
sudo apt update && sudo apt upgrade -y

# Docker образы
docker-compose pull
docker-compose up -d
```

### Смена секретных ключей

1. Отредактируйте `.env`
2. Перезапустите сервисы: `make restart`

### Мониторинг безопасности

```bash
# Fail2ban статус
sudo fail2ban-client status

# Последние попытки входа
sudo lastb

# Открытые порты
sudo netstat -tulpn
```

## Дополнительная настройка

### Email уведомления (опционально)

Добавьте в `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Backup автоматизация

Создайте cron задачу:

```bash
crontab -e
```

Добавьте:

```cron
# Бэкап каждый день в 3:00
0 3 * * * cd /root/crm-mydoc && make backup
```

### Мониторинг (Prometheus + Grafana)

Добавьте в `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

## Контакты поддержки

- Email: admin@it-mydoc.ru
- Документация: /root/crm-mydoc/README.md
- Архитектура: /root/crm-mydoc/ARCHITECTURE.md

## Чеклист успешного деплоя

- [ ] DNS настроен и работает
- [ ] Сервер подготовлен (setup-server.sh)
- [ ] .env файл создан и заполнен
- [ ] Все контейнеры запущены (docker-compose ps)
- [ ] SSL сертификат получен
- [ ] Администратор создан
- [ ] Веб-интерфейс доступен
- [ ] Telegram бот работает
- [ ] Настроен регулярный бэкап







