#!/bin/bash

echo "=== Monitor de Sistema PIEVDCS ==="
echo "Iniciado em: $(date)"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arquivo de log
LOG_FILE="monitor_$(date +%Y%m%d_%H%M%S).log"

# Função para logging
log_metric() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Loop de monitoramento
INTERVAL=2  # segundos entre cada coleta
DURATION=300  # duração total em segundos (5 minutos)
ITERATIONS=$((DURATION / INTERVAL))

for i in $(seq 1 $ITERATIONS); do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    
    # Memória
    MEM_INFO=$(free | grep Mem)
    MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
    MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
    MEM_PERCENT=$(awk "BEGIN {printf \"%.2f\", ($MEM_USED/$MEM_TOTAL)*100}")
    
    # Disco
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    # Processos Django/Gunicorn
    DJANGO_PROCS=$(ps aux | grep -E 'gunicorn|django|uwsgi' | grep -v grep | wc -l)
    
    # Conexões de rede
    CONNECTIONS=$(netstat -an | grep :8000 | wc -l)
    ESTABLISHED=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l)
    TIME_WAIT=$(netstat -an | grep :8000 | grep TIME_WAIT | wc -l)
    
    # Load Average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
    
    # Output colorido
    log_metric "[$TIMESTAMP] Iteração $i/$ITERATIONS"
    log_metric "${GREEN}CPU: ${CPU_USAGE}%${NC} | ${YELLOW}MEM: ${MEM_PERCENT}%${NC} | DISK: ${DISK_USAGE}%"
    log_metric "Django Processes: $DJANGO_PROCS | Connections: $ESTABLISHED/$CONNECTIONS | TIME_WAIT: $TIME_WAIT"
    log_metric "Load Average:$LOAD_AVG"
    log_metric "---"
    
    # Alertas
    if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
        log_metric "${RED}ALERTA: CPU acima de 80%!${NC}"
    fi
    
    if (( $(echo "$MEM_PERCENT > 80" | bc -l) )); then
        log_metric "${RED}ALERTA: Memória acima de 80%!${NC}"
    fi
    
    if [ $ESTABLISHED -gt 100 ]; then
        log_metric "${YELLOW}AVISO: Muitas conexões estabelecidas ($ESTABLISHED)${NC}"
    fi
    
    sleep $INTERVAL
done

echo ""
echo "=== Monitoramento concluído ==="
echo "Log salvo em: $LOG_FILE"

# Gerar resumo
echo ""
echo "=== RESUMO ==="
grep "CPU:" "$LOG_FILE" | awk -F'CPU: |%' '{sum+=$2; count++} END {print "CPU Média: " sum/count "%"}'
grep "MEM:" "$LOG_FILE" | awk -F'MEM: |%' '{sum+=$2; count++} END {print "Memória Média: " sum/count "%"}'
grep "ALERTA" "$LOG_FILE" || echo "Nenhum alerta crítico"
