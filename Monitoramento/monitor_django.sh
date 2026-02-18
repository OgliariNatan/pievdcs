#!/bin/bash

echo "=== Monitor Django/Gunicorn ==="

LOG_FILE="django_monitor_$(date +%Y%m%d_%H%M%S).log"

monitor_django() {
    while true; do
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        
        # Workers ativos
        WORKERS=$(ps aux | grep gunicorn | grep -v grep | wc -l)
        
        # Uso de memória por worker
        MEM_USAGE=$(ps aux | grep gunicorn | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
        
        # Threads
        THREADS=$(ps -eLf | grep gunicorn | grep -v grep | wc -l)
        
        # Conexões TCP
        TCP_CONN=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l)
        
        echo "[$TIMESTAMP] Workers: $WORKERS | Mem: ${MEM_USAGE}MB | Threads: $THREADS | Conexao: $TCP_CONN" | tee -a "$LOG_FILE"
        
        # Verificar workers travados (exemplo)
        ps aux | grep gunicorn | grep -v grep | awk '{if($3 > 50) print "ALERTA: Worker PID "$2" com CPU alta: "$3"%"}' | tee -a "$LOG_FILE"
        
        sleep 2
    done
}

monitor_django
