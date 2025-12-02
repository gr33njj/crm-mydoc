# 🚀 НАЧНИТЕ ЗДЕСЬ - CRM MyDoctor

## ✅ Система готова к деплою!

Все компоненты созданы и настроены. Следуйте этим шагам:

---

## 📋 Что уже готово:

✅ **Backend API (FastAPI + PostgreSQL)**
- REST API с полной функциональностью
- Аутентификация JWT
- CRUD операции для всех сущностей
- Система уведомлений

✅ **Frontend (Next.js PWA)**
- Mobile-first дизайн
- PWA поддержка
- Страницы логина и дашборда
- Real-time обновления

✅ **Telegram Bot**
- Команды для работы с задачами
- Система уведомлений
- Привязка аккаунтов

✅ **Система отчётов**
- Генерация narrative-стиля отчётов
- Фильтры по периодам и отделам
- Скачивание в текстовом формате

✅ **Корпоративный чат**
- Личные и групповые чаты
- Real-time сообщения
- Файлы и ответы

✅ **Docker + Nginx + SSL**
- Полная контейнеризация
- Автоматическое получение SSL
- Production-ready конфигурация

---

## 🎯 Шаги для запуска (15 минут):

### Шаг 1: Получите Telegram Bot Token

1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте `/newbot`
4. Следуйте инструкциям
5. **Скопируйте токен** (формат: `1234567890:ABCdef...`)

### Шаг 2: Настройте окружение

```bash
cd /root/crm-mydoc

# Скопируйте пример
cp .env.example .env

# Откройте для редактирования
nano .env
```

**Измените эти строки:**
```env
SECRET_KEY=придумайте-случайную-строку-минимум-32-символа-например-qwerty12345678901234567890qwerty12
TELEGRAM_BOT_TOKEN=ваш-токен-от-botfather
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 3: Подготовьте сервер

```bash
chmod +x setup-server.sh
./setup-server.sh
```

**ВАЖНО:** После завершения перезайдите:
```bash
logout
# Затем снова подключитесь
ssh root@91.218.112.231
```

### Шаг 4: Запустите деплой

```bash
cd /root/crm-mydoc
chmod +x deploy.sh
./deploy.sh
```

Когда спросит про SSL сертификат:
- Введите `y` если DNS настроен (обычно да)
- Введите `n` если хотите настроить позже

### Шаг 5: Создайте администратора

```bash
make admin
```

Введите данные:
- **Email:** admin@it-mydoc.ru (или ваш)
- **Имя:** Администратор
- **Пароль:** (минимум 6 символов)
- **Телефон:** (опционально)

---

## 🎉 Готово! Проверьте работу:

### 1. Веб-интерфейс
Откройте: **https://crm.it-mydoc.ru**

Войдите с учётными данными администратора.

### 2. Telegram Bot
1. Найдите вашего бота в Telegram (имя указано при создании)
2. Отправьте `/start`
3. Привяжите аккаунт: `/register admin@it-mydoc.ru`
4. Попробуйте: `/tasks`, `/help`

### 3. Проверка сервисов
```bash
docker-compose ps
```

Все должны быть в статусе **"Up"**.

---

## 📚 Документация:

- **QUICKSTART.md** - Краткая инструкция
- **DEPLOYMENT_GUIDE.md** - Полное руководство по деплою
- **README.md** - Общая документация
- **ARCHITECTURE.md** - Архитектура системы

---

## 🛠️ Полезные команды:

```bash
# Просмотр логов
make logs

# Перезапуск
make restart

# Создать админа
make admin

# Бэкап БД
make backup

# Статус
docker-compose ps

# Остановка
docker-compose down

# Запуск
docker-compose up -d
```

---

## 🆘 Помощь:

### Проблема: Сервисы не запускаются
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Проблема: SSL не получен
1. Проверьте DNS: `nslookup crm.it-mydoc.ru`
2. Должен показать IP: 91.218.112.231
3. Повторите получение сертификата:
```bash
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@it-mydoc.ru \
  --agree-tos \
  --no-eff-email \
  -d crm.it-mydoc.ru
docker-compose restart nginx
```

### Проблема: Бот не отвечает
```bash
docker-compose logs -f telegram_bot
# Проверьте токен в .env
# Перезапустите: docker-compose restart telegram_bot
```

---

## 📊 Структура системы:

```
CRM MyDoctor
├── Backend (FastAPI)    :8000
├── Frontend (Next.js)   :3000
├── PostgreSQL          :5432
├── Redis               :6379
├── Telegram Bot
└── Nginx (SSL)         :80, :443
```

---

## 🔐 Безопасность:

✅ HTTPS (SSL Let's Encrypt)
✅ JWT аутентификация
✅ RBAC (роли)
✅ Password hashing (bcrypt)
✅ Firewall (UFW)
✅ Fail2ban защита
✅ Rate limiting

---

## 📞 Контакты:

- **Сервер:** 91.218.112.231
- **Домен:** crm.it-mydoc.ru
- **Email:** admin@it-mydoc.ru

---

## ⚡ Быстрый чеклист:

- [ ] Telegram Bot Token получен
- [ ] .env файл настроен
- [ ] setup-server.sh выполнен (и перезашли)
- [ ] deploy.sh выполнен
- [ ] SSL сертификат получен
- [ ] Администратор создан (make admin)
- [ ] Сайт открывается
- [ ] Telegram бот отвечает

---

**Если всё работает - поздравляем! Система готова к использованию! 🎉**

Для добавления пользователей используйте веб-интерфейс (раздел "Пользователи" в админке).







