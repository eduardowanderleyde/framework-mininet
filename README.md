# Framework Mininet-WiFi para Simulação de Redes Mesh

Framework completo para simulação de redes Wi-Fi mesh realistas usando Mininet-WiFi, com foco em mobilidade, interferência e análise de performance.

## 🚀 Funcionalidades

- **Cenários Realistas**: Simulações de redes mesh Wi-Fi com mobilidade
- **Logs Estruturados**: Dados CSV com RSSI, distância, latência e conectividade
- **Análise Avançada**: Ferramenta de análise com gráficos e estatísticas
- **Testes de Performance**: Throughput e conectividade automatizados
- **Mobilidade Dinâmica**: Movimento realista de dispositivos

## 📁 Estrutura do Projeto

```
framework-mininet/
├── scenarios/                 # Cenários de simulação
│   ├── basic_wifi.py         # Cenário básico Wi-Fi
│   ├── mesh_mobility.py      # Rede mesh com mobilidade
│   ├── interference_test.py  # Teste de interferência
│   ├── sdn_wifi_test.py      # Validação SDN
│   ├── rasp_car_scan.py      # 🎯 Rasp-Car Scanner
│   └── rasp_car_rout_scan.py # 🎯 Rasp-Car-Rout (móvel)
├── tools/                    # Ferramentas auxiliares
│   ├── install_mininet.py    # Instalação automatizada
│   ├── throughput_test.py    # Teste de throughput
│   └── analyze_logs.py       # 📊 Análise de logs CSV
├── logs/                     # Logs gerados
├── requirements.txt          # Dependências Python
└── README.md                # Este arquivo
```

## 🎯 Cenários Principais

### 1. Rasp-Car Scanner
- **Modem principal**: AP fixo (recebe internet)
- **2 roteadores mesh**: Fixos, formam rede mesh
- **Raspberry Pi**: Móvel, escaneia sinais Wi-Fi
- **Logs**: CSV com RSSI, distância, latência, conectividade

### 2. Rasp-Car-Rout
- **Modem principal**: AP fixo
- **1 roteador mesh fixo**: mesh1
- **1 roteador mesh móvel**: mesh2 (move junto com Raspberry)
- **Raspberry Pi**: Móvel, sincronizado com mesh2

## 🛠️ Instalação

### Pré-requisitos
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip git

# Dependências Python
pip3 install -r requirements.txt
```

### Instalação do Mininet-WiFi
```bash
# Instalação automatizada
python3 tools/install_mininet.py

# Ou instalação manual
git clone https://github.com/intrig-unicamp/mininet-wifi.git
cd mininet-wifi
sudo util/install.sh -Wlnfv
```

## 🚀 Como Usar

### 1. Executar Cenários
```bash
# Configurar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.*/dist-packages

# Rasp-Car Scanner
python3 scenarios/rasp_car_scan.py

# Rasp-Car-Rout (móvel)
python3 scenarios/rasp_car_rout_scan.py
```

### 2. Analisar Logs
```bash
# Análise completa com gráficos
python3 tools/analyze_logs.py rasp_car_log.csv

# Análise sem gráficos
python3 tools/analyze_logs.py rasp_car_rout_log.csv --no-plots
```

### 3. Teste de Throughput
```bash
# Teste manual
python3 tools/throughput_test.py

# Ou usar iperf diretamente
iperf -s  # Servidor
iperf -c <IP>  # Cliente
```

## 📊 Logs e Análise

### Estrutura dos Logs CSV
```csv
timestamp,position,ap,rssi,distance,latency,connected
1703123456.789,15.0,25.0,0.0,modem,-45.23,5.5,15.5,YES
1703123458.789,35.0,30.0,0.0,mesh1,-52.67,25.3,7.53,YES
```

### Métricas Coletadas
- **RSSI**: Intensidade do sinal (dBm)
- **Distância**: Distância até o AP (metros)
- **Latência**: Latência simulada (ms)
- **Conectividade**: Status de conexão (YES/NO)
- **Posição**: Coordenadas X,Y,Z do dispositivo

### Análise Automática
A ferramenta `analyze_logs.py` gera:
- 📈 Gráfico de RSSI ao longo do tempo
- 📊 Performance por Access Point
- 🗺️ Caminho de mobilidade
- 📋 Estatísticas detalhadas

## 🔧 Configurações Avançadas

### Ajustar Range dos APs
```python
# Nos cenários, alterar o parâmetro 'range'
modem = net.addAccessPoint('modem', ..., range=58)  # 58 metros
```

### Modificar Modelo de Propagação
```python
# Modelo log-distance com expoente personalizado
net.setPropagationModel(model="logDistance", exp=3.5)
```

### Configurar Canais Wi-Fi
```python
# Canais não sobrepostos para evitar interferência
modem = net.addAccessPoint('modem', ..., channel='1')   # 2.412 GHz
mesh1 = net.addAccessPoint('mesh1', ..., channel='6')   # 2.437 GHz
mesh2 = net.addAccessPoint('mesh2', ..., channel='11')  # 2.462 GHz
```

## 📈 Melhorias Implementadas

### ✅ Concluídas
- [x] Range dos APs ajustado para 58m
- [x] Cálculo de RSSI realista baseado em modelo de propagação
- [x] Métricas adicionais: distância, latência, conectividade
- [x] Configuração de conectividade entre dispositivos
- [x] Teste de throughput automatizado
- [x] Ferramenta de análise de logs com gráficos
- [x] Logs estruturados em CSV

### 🔄 Próximas Melhorias
- [ ] Simulação de obstáculos e paredes
- [ ] Modelo de interferência mais realista
- [ ] Handoff automático entre APs
- [ ] Interface web para visualização
- [ ] Mais cenários de teste

## 🐛 Solução de Problemas

### Erro: "No module named 'mininet.wifi'"
```bash
# Usar 'mn_wifi' em vez de 'mininet.wifi'
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
```

### Erro: "enable_interference not supported"
```bash
# Remover parâmetro enable_interference
net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
```

### Erro: "iperf not found"
```bash
# Instalar iperf
sudo apt install iperf
```

## 📝 Exemplos de Uso

### Cenário Básico
```bash
# Executar cenário básico
python3 scenarios/basic_wifi.py
```

### Teste de Interferência
```bash
# Executar teste de interferência
python3 scenarios/interference_test.py
```

### Análise Comparativa
```bash
# Comparar performance dos dois cenários
python3 tools/analyze_logs.py rasp_car_log.csv
python3 tools/analyze_logs.py rasp_car_rout_log.csv
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Eduardo Wanderley**
- GitHub: [@eduardowanderleyde](https://github.com/eduardowanderleyde)

## 🙏 Agradecimentos

- Mininet-WiFi Team
- Comunidade OpenFlow/SDN
- Contribuidores do projeto

---

**Última atualização**: Dezembro 2024
**Versão**: 2.0 - Com melhorias de análise e logs estruturados 