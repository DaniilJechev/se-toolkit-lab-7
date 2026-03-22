# Lab 7 - Пошаговая настройка на VM

Подключитесь к VM: `ssh root@10.93.26.28`

## Шаг 1: Остановить Lab 6
```bash
cd ~/se-toolkit-lab-6 && docker compose --env-file .env.docker.secret down
cd ~
```

## Шаг 2: Настроить Docker DNS
```bash
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker
```

## Шаг 3: Клонировать репозиторий
```bash
git clone https://github.com/DaniilJechev/se-toolkit-lab-7 ~/se-toolkit-lab-7
cd ~/se-toolkit-lab-7
```

## Шаг 4: Создать .env.docker.secret
```bash
cp .env.docker.example .env.docker.secret
nano .env.docker.secret
```

**Отредактируйте следующие строки:**
```
AUTOCHECKER_EMAIL=d.zhechev@innopolis.university
AUTOCHECKER_PASSWORD=DaniilJechevBFG9KGG
LMS_API_KEY=my-secret-api-key
```

## Шаг 5: Создать .env.bot.secret
```bash
cp .env.bot.example .env.bot.secret
nano .env.bot.secret
```

**Заполните (LMS_API_KEY должно совпадать с .env.docker.secret):**
```
BOT_TOKEN=8478154544:AAEkQI7yU5YQOsPBLJ_xTmxo5bYJcZfPboE
LMS_API_URL=http://localhost:42002
LMS_API_KEY=my-secret-api-key
LLM_API_KEY=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
LLM_API_BASE_URL=https://openrouter.ai/api/v1
LLM_API_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

## Шаг 6: Запустить сервисы
```bash
docker compose --env-file .env.docker.secret up --build -d
```

Подождите 30 секунд, затем проверьте:
```bash
docker compose --env-file .env.docker.secret ps
```

## Шаг 7: Синхронизировать данные
```bash
curl -X POST http://localhost:42002/pipeline/sync \
    -H "Authorization: Bearer my-secret-api-key" \
    -H "Content-Type: application/json" \
    -d '{}'
```

Проверьте данные:
```bash
curl -s http://localhost:42002/items/ -H "Authorization: Bearer my-secret-api-key" | head -c 200
```

## Шаг 8: Проверка LLM (OpenRouter)

Так как вы используете OpenRouter, проверьте что LLM работает:

```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer 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" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/nemotron-3-super-120b-a12b:free","messages":[{"role":"user","content":"What is 2+2?"}]}' | head -c 150
```

Должен вернуться JSON с ответом "4" или похожим.

---

**Примечание:** Если вы хотите использовать Qwen Code API на VM (локально), выполните:
```bash
cd ~ && git clone https://github.com/innopolis-universe/se-toolkit-qwen-code-oai-proxy.git qwen-code-oai-proxy
cd ~/qwen-code-oai-proxy && cp .env.example .env
nano .env  # установите QWEN_API_KEY
docker compose up -d
```
И измените в `.env.bot.secret`:
```
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```

## Шаг 9: Финальная проверка
```bash
# Backend
curl -s http://localhost:42002/ | head -c 50

# LLM (OpenRouter)
curl -s https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer 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" | head -c 100
```
