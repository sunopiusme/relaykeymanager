#!/bin/bash
#
# Relay Beta Bot — автозапуск с перезапуском при падении
#
# Первый запуск:
#   chmod +x run.sh
#   ./run.sh setup    # установка + генерация ключей
#
# Обычный запуск:
#   ./run.sh
#
# Остановка:
#   ./run.sh stop
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/.bot.pid"
LOG_FILE="$SCRIPT_DIR/bot.log"
ENV_FILE="$SCRIPT_DIR/.env"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

# Загрузка .env если есть
load_env() {
    if [ -f "$ENV_FILE" ]; then
        export $(grep -v '^#' "$ENV_FILE" | xargs)
        log "Loaded .env"
    fi
}

# Первоначальная настройка
setup() {
    log "Setting up Relay Beta Bot..."
    
    # Python venv
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    log "Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Генерация ключей если нет
    if [ ! -f "$ENV_FILE" ] || ! grep -q "RELAY_BETA_SIGNING_KEY" "$ENV_FILE"; then
        log "Generating Ed25519 keys..."
        
        # Запускаем crypto.py и парсим вывод
        KEYS=$(python3 crypto.py 2>/dev/null)
        PRIVATE_KEY=$(echo "$KEYS" | grep "Private key" | cut -d: -f2 | tr -d ' ')
        PUBLIC_KEY=$(echo "$KEYS" | grep "Public key" | cut -d: -f2 | tr -d ' ')
        
        if [ -n "$PRIVATE_KEY" ]; then
            echo "" >> "$ENV_FILE"
            echo "# Generated $(date)" >> "$ENV_FILE"
            echo "RELAY_BETA_SIGNING_KEY=$PRIVATE_KEY" >> "$ENV_FILE"
            echo "RELAY_BETA_PUBLIC_KEY=$PUBLIC_KEY" >> "$ENV_FILE"
            log "Keys saved to .env"
            echo ""
            warn "PUBLIC KEY (add to Swift app):"
            echo "$PUBLIC_KEY"
            echo ""
        fi
    fi
    
    # Проверка токена
    if [ ! -f "$ENV_FILE" ] || ! grep -q "TELEGRAM_BOT_TOKEN" "$ENV_FILE"; then
        echo ""
        warn "Bot token not found!"
        echo "Get it from @BotFather and add to .env:"
        echo ""
        echo "  echo 'TELEGRAM_BOT_TOKEN=your_token' >> .env"
        echo ""
    fi
    
    log "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Add TELEGRAM_BOT_TOKEN to .env"
    echo "  2. Run: ./run.sh"
}

# Запуск бота
start_bot() {
    load_env
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "YOUR_BOT_TOKEN_HERE" ]; then
        error "TELEGRAM_BOT_TOKEN not set!"
        echo "Add to .env: TELEGRAM_BOT_TOKEN=your_token"
        exit 1
    fi
    
    # Активируем venv если есть
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    log "Starting Relay Beta Bot..."
    
    # Бесконечный цикл с перезапуском
    while true; do
        python3 telegram_beta_bot.py 2>&1 | tee -a "$LOG_FILE"
        
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 0 ]; then
            log "Bot stopped gracefully"
            break
        fi
        
        warn "Bot crashed (exit code: $EXIT_CODE). Restarting in 5s..."
        sleep 5
    done
}

# Запуск в фоне
start_daemon() {
    load_env
    
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            warn "Bot already running (PID: $OLD_PID)"
            exit 0
        fi
    fi
    
    log "Starting bot in background..."
    nohup "$0" run >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    log "Bot started (PID: $!)"
    echo "Logs: tail -f $LOG_FILE"
}

# Остановка
stop_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "Stopping bot (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            log "Bot stopped"
        else
            warn "Bot not running"
            rm "$PID_FILE"
        fi
    else
        warn "No PID file found"
    fi
}

# Статус
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "Bot running (PID: $PID)"
            echo "Logs: tail -f $LOG_FILE"
        else
            warn "Bot not running (stale PID file)"
        fi
    else
        warn "Bot not running"
    fi
}

# Логи
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        warn "No log file yet"
    fi
}

# Main
case "${1:-daemon}" in
    setup)
        setup
        ;;
    run)
        start_bot
        ;;
    daemon|start|"")
        start_daemon
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 1
        start_daemon
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|status|logs}"
        exit 1
        ;;
esac
