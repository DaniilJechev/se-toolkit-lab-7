#!/bin/bash
# Скрипт настройки Lab 7 на VM
# Выполните от root: bash ~/vm-setup.sh

set -e

GITHUB_USER="DaniilJechev"
REPO_URL="https://github.com/${GITHUB_USER}/se-toolkit-lab-7"
VM_DIR=~/se-toolkit-lab-7

echo "=== Lab 7 VM Setup ==="

# 1. Остановить Lab 6
echo "[1/7] Остановка Lab 6..."
if [ -d ~/se-toolkit-lab-6 ]; then
    cd ~/se-toolkit-lab-6
    docker compose --env-file .env.docker.secret down 2>/dev/null || true
    cd ~
fi

# 2. Настроить DNS для Docker
echo "[2/7] Настройка Docker DNS..."
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker

# 3. Клонировать репозиторий
echo "[3/7] Клонирование репозитория..."
if [ -d "$VM_DIR" ]; then
    echo "Репозиторий уже существует, обновляем..."
    cd "$VM_DIR"
    git pull origin main || true
    cd ~
else
    git clone "$REPO_URL" "$VM_DIR"
fi

# 4. Создать .env.docker.secret
echo "[4/7] Создание .env.docker.secret..."
cd "$VM_DIR"
cp .env.docker.example .env.docker.secret

# Заменить значения в .env.docker.secret
sed -i 's|LMS_API_KEY=my-secret-api-key|LMS_API_KEY=my-secret-api-key|g' .env.docker.secret
sed -i 's|AUTOCHECKER_API_LOGIN=<autochecker-api-login>|AUTOCHECKER_API_LOGIN=d.zhechev@innopolis.university|g' .env.docker.secret
sed -i 's|AUTOCHECKER_API_PASSWORD=<autochecker-api-password>|AUTOCHECKER_API_PASSWORD=DaniilJechevBFG9KGG|g' .env.docker.secret

# 5. Создать .env.bot.secret
echo "[5/7] Создание .env.bot.secret..."
cp .env.bot.example .env.bot.secret

sed -i 's|LMS_API_KEY=my-secret-api-key|LMS_API_KEY=my-secret-api-key|g' .env.bot.secret
sed -i 's|BOT_TOKEN=your-telegram-bot-token-here|BOT_TOKEN=8478154544:AAEkQI7yU5YQOsPBLJ_xTmxo5bYJcZfPboE|g' .env.bot.secret
sed -i 's|LLM_API_KEY=my-secret-qwen-key|LLM_API_KEY=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|g' .env.bot.secret
sed -i 's|LLM_API_BASE_URL=http://localhost:42005/v1|LLM_API_BASE_URL=https://openrouter.ai/api/v1|g' .env.bot.secret
sed -i 's|LLM_API_MODEL=coder-model|LLM_API_MODEL=nvidia/nemotron-3-super-120b-a12b:free|g' .env.bot.secret

# 6. Запустить сервисы
echo "[6/7] Запуск Docker сервисов..."
docker compose --env-file .env.docker.secret down -v 2>/dev/null || true
docker compose --env-file .env.docker.secret up --build -d

echo "Ожидание запуска сервисов (30 сек)..."
sleep 30

# 7. Синхронизация данных
echo "[7/7] Синхронизация данных ETL..."
LMS_API_KEY=$(grep "^LMS_API_KEY=" .env.docker.secret | cut -d'=' -f2)
curl -X POST http://localhost:42002/pipeline/sync \
    -H "Authorization: Bearer ${LMS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{}'

echo ""
echo "=== Проверка сервисов ==="
docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"

echo ""
echo "Проверка backend (порт 42002):"
curl -s http://localhost:42002/items/ -H "Authorization: Bearer ${LMS_API_KEY}" | head -c 100
echo ""

echo ""
echo "=== Настройка Qwen Code API ==="
echo "Если Qwen proxy ещё не настроен, выполните:"
echo "  cd ~ && git clone https://github.com/innopolis-universe/se-toolkit-qwen-code-oai-proxy.git qwen-code-oai-proxy"
echo "  cd ~/qwen-code-oai-proxy"
echo "  cp .env.example .env"
echo "  nano .env  # установите QWEN_API_KEY"
echo "  docker compose up -d"
echo ""
echo "ИЛИ используйте OpenRouter (см. инструкцию)"

echo ""
echo "=== Setup завершён ==="
