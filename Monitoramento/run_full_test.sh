#!/bin/bash

echo "======================================"
echo "  Teste de Carga Completo - PIEVDCS  "
echo "======================================"
echo ""

# Criar diretório para resultados
RESULTS_DIR="test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"
cd "$RESULTS_DIR"

echo "Resultados serão salvos em: $RESULTS_DIR"
echo ""

# 1. Iniciar monitor de sistema em background
echo "[1/4] Iniciando monitor de sistema..."
bash ../monitor_sistema.sh &
MONITOR_PID=$!

# 2. Iniciar monitor Django em background
echo "[2/4] Iniciando monitor Django..."
bash ../monitor_django.sh &
DJANGO_MONITOR_PID=$!

# Aguardar inicialização
sleep 3

# 3. Executar teste de carga
echo "[3/4] Executando teste de carga..."
bash ../test_carga_avancado.sh

# 4. Parar monitores
echo "[4/4] Finalizando monitores..."
kill $MONITOR_PID 2>/dev/null
kill $DJANGO_MONITOR_PID 2>/dev/null

echo ""
echo "======================================"
echo "  Teste Concluído!                   "
echo "======================================"
echo ""
echo "Verifique os resultados em: $RESULTS_DIR"
ls -lh

# Gerar relatório HTML (opcional)
cat > relatorio.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Teste - PIEVDCS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        .metric { background: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4caf50; }
        .alert { background: #ffebee; border-left: 4px solid #f44336; }
    </style>
</head>
<body>
    <h1>Relatório de Teste de Carga</h1>
    <p><strong>Data:</strong> $(date)</p>
    
    <h2>Resultados do Teste</h2>
    <pre>$(cat resultados_*.txt)</pre>
    
    <h2>Monitoramento do Sistema</h2>
    <pre>$(tail -50 monitor_*.log)</pre>
</body>
</html>
EOF

echo "Relatório HTML gerado: relatorio.html"
