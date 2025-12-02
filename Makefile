.PHONY: help setup deploy start stop restart logs ps build clean backup restore admin

help:
	@echo "CRM MyDoctor - Makefile команды"
	@echo ""
	@echo "Основные:"
	@echo "  make setup     - Подготовить сервер"
	@echo "  make deploy    - Деплой приложения"
	@echo "  make start     - Запустить все сервисы"
	@echo "  make stop      - Остановить все сервисы"
	@echo "  make restart   - Перезапустить все сервисы"
	@echo ""
	@echo "Мониторинг:"
	@echo "  make logs      - Показать логи всех сервисов"
	@echo "  make ps        - Показать статус контейнеров"
	@echo ""
	@echo "Разработка:"
	@echo "  make build     - Пересобрать контейнеры"
	@echo "  make clean     - Удалить все контейнеры и volumes"
	@echo ""
	@echo "Администрирование:"
	@echo "  make admin     - Создать администратора"
	@echo "  make backup    - Создать бэкап БД"
	@echo "  make restore   - Восстановить БД из бэкапа"

setup:
	@echo "🔧 Подготовка сервера..."
	@chmod +x setup-server.sh
	@./setup-server.sh

deploy:
	@echo "🚀 Деплой приложения..."
	@chmod +x deploy.sh
	@./deploy.sh

start:
	@echo "▶️  Запуск сервисов..."
	@docker-compose up -d

stop:
	@echo "⏹️  Остановка сервисов..."
	@docker-compose down

restart:
	@echo "🔄 Перезапуск сервисов..."
	@docker-compose restart

logs:
	@docker-compose logs -f

ps:
	@docker-compose ps

build:
	@echo "🔨 Пересборка контейнеров..."
	@docker-compose up -d --build

clean:
	@echo "🧹 Удаление контейнеров и volumes..."
	@docker-compose down -v
	@docker system prune -f

backup:
	@echo "💾 Создание бэкапа БД..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U mydoc_user mydoc_crm > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Бэкап создан: backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

restore:
	@echo "⚠️  Восстановление БД из бэкапа"
	@echo "Доступные бэкапы:"
	@ls -lh backups/
	@read -p "Введите имя файла бэкапа: " backup_file; \
	docker-compose exec -T postgres psql -U mydoc_user mydoc_crm < backups/$$backup_file
	@echo "✅ БД восстановлена"

admin:
	@echo "👤 Создание администратора..."
	@docker-compose exec backend python init-admin.py

logs-backend:
	@docker-compose logs -f backend

logs-frontend:
	@docker-compose logs -f frontend

logs-bot:
	@docker-compose logs -f telegram_bot

logs-nginx:
	@docker-compose logs -f nginx







