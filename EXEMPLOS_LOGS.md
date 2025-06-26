# 📊 Exemplos de Logs Gerados

Este documento mostra os diferentes formatos e exemplos de logs gerados pelos cenários do framework Mininet-WiFi.

## 📁 Arquivos de Log Disponíveis

### 1. **rasp_car_scan_log.csv** (574 bytes)
- **Formato**: CSV básico
- **Registros**: 10
- **Colunas**: timestamp, position, ap, rssi, distance, latency, connected
- **Cenário**: Rasp-Car Scanner básico

### 2. **rasp_car_rout_scan_log.csv** (572 bytes)
- **Formato**: CSV básico
- **Registros**: 10
- **Colunas**: timestamp, position, ap, rssi, distance, latency, connected
- **Cenário**: Rasp-Car-Rout (com roteador móvel)

### 3. **rasp_car_scan_extended_log.csv** (1.3KB)
- **Formato**: CSV estendido
- **Registros**: 20
- **Colunas**: timestamp, position, ap, rssi, distance, latency, connected, signal_quality
- **Cenário**: Rasp-Car Scanner com mais dados e qualidade de sinal

### 4. **rasp_car_json_log.json** (20KB)
- **Formato**: JSON estruturado
- **Registros**: 15
- **Estrutura**: Dados hierárquicos com metadados
- **Cenário**: Rasp-Car Scanner com log JSON

## 📋 Exemplos de Dados

### CSV Básico (rasp_car_scan_log.csv)
```csv
timestamp,position,ap,rssi,distance,latency,connected
1750967583.5071225,"0,0,0",modem,9.95,0.01,5.0,YES
1750967585.5074959,"0,0,0",modem,9.95,0.01,5.0,YES
1750967587.5077786,"0,0,0",modem,9.95,0.01,5.0,YES
```

### CSV Estendido (rasp_car_scan_extended_log.csv)
```csv
timestamp,position,ap,rssi,distance,latency,connected,signal_quality
1750968010.0047328,"0,0,0",modem,9.95,0.01,5.0,YES,EXCELLENT
1750968011.0053911,"0,0,0",modem,9.95,0.01,5.0,YES,EXCELLENT
1750968012.00569,"0,0,0",modem,9.95,0.01,5.0,YES,EXCELLENT
```

### JSON Estruturado (rasp_car_json_log.json)
```json
{
  "scenario": "rasp_car_json_log",
  "description": "Raspberry Pi mobile scanning with JSON logging",
  "total_iterations": 15,
  "logs": [
    {
      "timestamp": 1750968115.9497573,
      "timestamp_readable": "2025-06-26 17:01:55",
      "iteration": 1,
      "position": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "available_aps": [
        {
          "name": "modem",
          "ssid": "Internet",
          "channel": "1",
          "rssi": 9.95,
          "distance": 0.01,
          "latency": 5.0,
          "connected": true,
          "signal_strength": "strong"
        }
      ],
      "best_ap": {
        "name": "modem",
        "ssid": "Internet",
        "channel": "1",
        "rssi": 9.95,
        "distance": 0.01,
        "latency": 5.0,
        "connected": true,
        "signal_strength": "strong"
      },
      "network_status": {
        "total_aps": 3,
        "connected_aps": 3,
        "best_signal": 9.95
      }
    }
  ]
}
```

## 📊 Estatísticas dos Logs

### Resumo Geral
- **Total de logs válidos**: 4
- **Total de registros**: 55
- **Formatos**: CSV (3), JSON (1)

### Métricas RSSI
- **RSSI Mínimo**: 9.95 dBm
- **RSSI Máximo**: 9.95 dBm
- **RSSI Médio**: 9.95 dBm

### Distribuição de Access Points
- **modem**: 55 registros (100%)
- **mesh1**: 0 registros
- **mesh2**: 0 registros

## 🎯 Como Usar os Exemplos

### 1. Análise com Python
```python
import pandas as pd
import json

# Ler CSV
df = pd.read_csv('rasp_car_scan_log.csv')
print(df.head())

# Ler JSON
with open('rasp_car_json_log.json', 'r') as f:
    data = json.load(f)
print(data['logs'][0])
```

### 2. Análise com Ferramenta do Framework
```bash
python3 tools/analyze_logs.py rasp_car_scan_log.csv
```

### 3. Visualização Geral
```bash
python3 show_all_logs.py
```

## 🔧 Scripts de Geração

### Cenários Disponíveis
1. **rasp_car_scan.py** - Cenário básico
2. **rasp_car_rout_scan.py** - Com roteador móvel
3. **rasp_car_scan_extended.py** - Versão estendida
4. **rasp_car_json_log.py** - Log em JSON

### Como Executar
```bash
# Usando o wrapper
python3 run_scenario.py rasp_car_scan

# Ou diretamente
sudo PYTHONPATH=/usr/local/lib/python3.12/dist-packages python3 scenarios/rasp_car_scan.py
```

## 📈 Próximos Passos

### Melhorias Sugeridas
1. **Variação de RSSI**: Implementar cálculo mais realista baseado na distância
2. **Handoff entre APs**: Simular mudança automática entre access points
3. **Interferência**: Adicionar modelo de interferência entre canais
4. **Obstáculos**: Simular paredes e obstáculos no ambiente
5. **Mais cenários**: Criar cenários com diferentes topologias

### Formatos Adicionais
- **XML**: Para integração com sistemas enterprise
- **YAML**: Para configurações e logs estruturados
- **Parquet**: Para análise de big data
- **SQLite**: Para armazenamento local estruturado

---

**Última atualização**: Junho 2024
**Framework**: Mininet-WiFi v2.6
**Total de exemplos**: 4 formatos diferentes 