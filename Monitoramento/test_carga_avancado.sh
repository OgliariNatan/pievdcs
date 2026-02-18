#!/bin/bash

echo "=== Teste de Carga PIEVDCS Avançado ==="
echo "Iniciando em: $(date)"
echo ""

URL="http://62.72.9.77:8000/"
TOTAL_REQUESTS=1000
CONCURRENT=50  # Recomendo começar menor

LOG_FILE="carga_$(date +%Y%m%d_%H%M%S).log"
RESULTS_FILE="resultados_$(date +%Y%m%d_%H%M%S).txt"

echo "URL: $URL" | tee "$RESULTS_FILE"
echo "Total Requests: $TOTAL_REQUESTS" | tee -a "$RESULTS_FILE"
echo "Concurrent: $CONCURRENT" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Arrays para estatísticas
declare -a response_times
declare -a response_codes

# Função para fazer uma requisição
make_request() {
    local id=$1
    start_time=$(date +%s.%N)
    response=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" --max-time 30 $URL)
    end_time=$(date +%s.%N)
    
    http_code=$(echo $response | cut -d'|' -f1)
    time_total=$(echo $response | cut -d'|' -f2)
    
    echo "$id|$http_code|$time_total" >> "$LOG_FILE"
    
    # Mostrar progresso a cada 100 requisições
    if [ $((id % 100)) -eq 0 ]; then
        echo "Progresso: $id/$TOTAL_REQUESTS requisições completadas"
    fi
}

export -f make_request
export URL
export LOG_FILE

# Iniciar teste
START_TIME=$(date +%s)

seq 1 $TOTAL_REQUESTS | xargs -P $CONCURRENT -I {} bash -c 'make_request {}'

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo "" | tee -a "$RESULTS_FILE"
echo "=== RESULTADOS ===" | tee -a "$RESULTS_FILE"
echo "Tempo total: ${TOTAL_TIME}s" | tee -a "$RESULTS_FILE"
echo "Requisições/segundo: $(echo "scale=2; $TOTAL_REQUESTS / $TOTAL_TIME" | bc)" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Análise dos resultados
echo "=== Códigos HTTP ===" | tee -a "$RESULTS_FILE"
awk -F'|' '{print $2}' "$LOG_FILE" | sort | uniq -c | sort -rn | tee -a "$RESULTS_FILE"

echo "" | tee -a "$RESULTS_FILE"
echo "=== Tempos de Resposta ===" | tee -a "$RESULTS_FILE"

# Estatísticas de tempo
awk -F'|' '{print $3}' "$LOG_FILE" | sort -n > /tmp/times.txt

MIN=$(head -1 /tmp/times.txt)
MAX=$(tail -1 /tmp/times.txt)
MEDIAN=$(awk '{a[i++]=$1} END{print a[int(i/2)]}' /tmp/times.txt)
AVG=$(awk '{sum+=$1} END {print sum/NR}' /tmp/times.txt)
P95=$(awk 'BEGIN{c=0} {a[c++]=$1} END{print a[int(c*0.95)]}' /tmp/times.txt)
P99=$(awk 'BEGIN{c=0} {a[c++]=$1} END{print a[int(c*0.99)]}' /tmp/times.txt)

echo "Mínimo: ${MIN}s" | tee -a "$RESULTS_FILE"
echo "Máximo: ${MAX}s" | tee -a "$RESULTS_FILE"
echo "Média: ${AVG}s" | tee -a "$RESULTS_FILE"
echo "Mediana: ${MEDIAN}s" | tee -a "$RESULTS_FILE"
echo "Percentil 95: ${P95}s" | tee -a "$RESULTS_FILE"
echo "Percentil 99: ${P99}s" | tee -a "$RESULTS_FILE"

# Taxa de erro
TOTAL=$(wc -l < "$LOG_FILE")
ERRORS=$(awk -F'|' '$2 != 200' "$LOG_FILE" | wc -l)
ERROR_RATE=$(echo "scale=2; ($ERRORS / $TOTAL) * 100" | bc)

echo "" | tee -a "$RESULTS_FILE"
echo "Taxa de erro: ${ERROR_RATE}%" | tee -a "$RESULTS_FILE"

rm /tmp/times.txt

echo ""
echo "Teste concluído em: $(date)"
echo "Resultados salvos em: $RESULTS_FILE"
echo "Log detalhado em: $LOG_FILE"
