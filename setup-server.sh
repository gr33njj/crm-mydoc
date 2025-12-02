#!/bin/bash
# Скрипт для подготовки Ubuntu сервера

set -e

echo "🔧 Подготовка Ubuntu сервера для CRM MyDoctor"
echo "=============================================="

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
echo "📦 Установка необходимых пакетов..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    fail2ban

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

# Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Установка Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

# Настройка firewall
echo "🔥 Настройка firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status

echo "✅ Firewall настроен"

# Настройка fail2ban
echo "🛡️  Настройка fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

echo "✅ Fail2ban настроен"

# Увеличение лимитов
echo "⚙️  Настройка системных лимитов..."
sudo tee -a /etc/security/limits.conf > /dev/null <<EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 4096
* hard nproc 4096
EOF

# Оптимизация sysctl
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# File system
fs.file-max = 2097152
EOF

sudo sysctl -p

echo "✅ Системные лимиты настроены"

# Создание swap (если нет)
if [ ! -f /swapfile ]; then
    echo "💾 Создание swap файла (2GB)..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ Swap создан"
else
    echo "✅ Swap уже существует"
fi

# Настройка автоматических обновлений безопасности
echo "🔐 Настройка автоматических обновлений безопасности..."
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

echo "✅ Автоматические обновления настроены"

# Создание пользователя для приложения (опционально)
if ! id "crm" &>/dev/null; then
    echo "👤 Создание пользователя crm..."
    sudo useradd -m -s /bin/bash crm
    sudo usermod -aG docker crm
    echo "✅ Пользователь crm создан"
else
    echo "✅ Пользователь crm уже существует"
fi

echo ""
echo "✅ Сервер подготовлен!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Перезайдите в систему для применения Docker прав"
echo "2. Клонируйте репозиторий проекта или загрузите файлы"
echo "3. Создайте .env файл на основе .env.example"
echo "4. Запустите ./deploy.sh для деплоя приложения"
echo ""
echo "⚠️  ВАЖНО: Перезайдите в систему командой:"
echo "   logout"
echo ""







