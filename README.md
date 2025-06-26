# Framework Mininet-WiFi para Simulação de Redes Mesh

Framework completo para simulação de redes Wi-Fi mesh realistas usando Mininet-WiFi, com foco em mobilidade, interferência e análise de performance.

## 🚀 Funcionalidades

- **Cenários Realistas**: Simulações de redes mesh Wi-Fi com mobilidade
- **Logs Estruturados**: Dados CSV com RSSI, distância, latência e conectividade
- **Análise Avançada**: Ferramenta de análise com gráficos e estatísticas
- **Testes de Performance**: Throughput e conectividade automatizados
- **Mobilidade Dinâmica**: Movimento realista de dispositivos
- **🌐 Interface Web**: Interface visual completa para executar cenários e visualizar resultados
- **📊 Progresso Visual**: Logs passo a passo com emojis e contadores de progresso
- **🔧 Script Wrapper**: Execução simplificada com configuração automática

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
├── templates/                # Templates da interface web
│   └── index.html           # Interface principal
├── web_interface.py         # 🌐 Servidor da interface web
├── start_interface.py       # 🚀 Script para iniciar interface
├── run_scenario.py          # 🔧 Script wrapper para executar cenários
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

### 3. 🎯 Mastering Scenario 1
- **Ambiente**: Espaço vazio 100m x 100m (sem obstáculos)
- **🔌 Roteador 1 (Backbone)**: Fixo em (0,0), conectado à internet via cabo
- **📡 Roteador 2 (Repetidor)**: Fixo em (50,50), repetidor mesh
- **🚗 Roteador 3 (Móvel)**: Em carrinho com rodas, se move entre waypoints
- **📱 Raspberry Pi**: No carrinho, escaneia qualidade da rede mesh
- **🎯 Trajetória**: Carrinho passa próximo aos roteadores para testar conectividade
- **📊 Métricas**: RSSI, distância, latência, throughput, handover, perda de pacotes

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

## 🌐 Interface Web (Recomendado)

### Como Usar a Interface Web

1. **Iniciar a Interface:**
```bash
python3 start_interface.py
```

2. **Acessar no Navegador:**
```
http://localhost:5000
```

3. **Executar Cenários:**
   - Clique em **"▶️ Executar"** no cenário desejado
   - Acompanhe o progresso em tempo real
   - Veja o log de execução ao vivo
   - Visualize os resultados gerados

4. **Recursos da Interface:**
   - ✅ **Execução Visual**: Clique e execute cenários
   - ✅ **Log em Tempo Real**: Veja o que está acontecendo
   - ✅ **Progresso Visual**: Barra de progresso em tempo real
   - ✅ **Visualização de Logs**: Veja os dados gerados
   - ✅ **Gráficos de Mobilidade**: Visualize o caminho percorrido
   - ✅ **Download de Logs**: Baixe os arquivos CSV/JSON

### Funcionalidades da Interface

- **🎯 Cenários Disponíveis**: Lista todos os cenários com descrições
- **⚡ Status de Execução**: Progresso e log em tempo real
- **📊 Logs Gerados**: Visualize, baixe e analise logs
- **📋 Visualizador de Dados**: Veja o conteúdo dos logs
- **🗺️ Gráficos de Mobilidade**: Visualize o caminho percorrido

## 🚀 Como Usar (Linha de Comando)

### 🔧 Script Wrapper (Recomendado)

O script `run_scenario.py` facilita a execução dos cenários com configuração automática do PYTHONPATH:

```bash
# Ver cenários disponíveis
python3 run_scenario.py --help

# Executar cenário Rasp-Car
python3 run_scenario.py rasp-car

# Executar cenário Rasp-Car-Rout
python3 run_scenario.py rasp-car-rout

# Executar outros cenários
python3 run_scenario.py basic
python3 run_scenario.py mesh
python3 run_scenario.py interference
python3 run_scenario.py sdn

# 🎯 Executar Mastering Scenario 1
python3 run_scenario.py mastering-1
```

**Vantagens do Script Wrapper:**
- ✅ **Configuração Automática**: PYTHONPATH configurado automaticamente
- ✅ **Execução Simplificada**: Comando único para executar cenários
- ✅ **Progresso Visual**: Logs passo a passo com emojis e contadores
- ✅ **Tratamento de Erros**: Mensagens claras de erro e ajuda
- ✅ **Execução com Sudo**: Gerencia automaticamente privilégios de root

### 📊 Exemplo de Saída com Progresso Visual

```
🎯 Framework Mininet-WiFi - Executor de Cenários
============================================================
🚀 Executando cenário: rasp-car
📁 Arquivo: scenarios/rasp_car_scan.py
🔧 PYTHONPATH configurado: /usr/local/lib/python3.12/dist-packages
============================================================
ℹ️  🚀 Iniciando simulação Rasp-Car Scanner...
ℹ️  📡 Criando rede Wi-Fi mesh...
ℹ️  🔌 Configurando modem principal...
ℹ️  🌐 Configurando roteadores mesh...
ℹ️  📱 Configurando Raspberry Pi móvel...
ℹ️  ⚙️  Configurando modelo de propagação...
ℹ️  🔨 Construindo rede...
ℹ️  🎮 Iniciando controlador...
ℹ️  📶 Ativando access points...
ℹ️  ✅ Rede Wi-Fi mesh ativada com sucesso!
ℹ️  🔄 Iniciando threads de mobilidade e escaneamento...
ℹ️  📊 Iniciando sistema de escaneamento e log...
ℹ️  🚗 Iniciando mobilidade do Raspberry Pi...
🔄 [10%] 🔍 Escaneando rede (ciclo 1/10)...
ℹ️  🟢 Posição: 15,25,0 | AP: modem | RSSI: -45.2 dBm | Dist: 5.5m | Lat: 5.6ms
🔄 [10%] 📍 Raspberry movido para: (15, 25, 0)
🔄 [20%] 🔍 Escaneando rede (ciclo 2/10)...
ℹ️  🟢 Posição: 35,30,0 | AP: mesh1 | RSSI: -52.7 dBm | Dist: 25.3m | Lat: 7.5ms
🔄 [20%] 📍 Raspberry movido para: (35, 30, 0)
...
ℹ️  💾 Log salvo em: rasp_car_scan_log.csv
ℹ️  🔐 Permissões do arquivo ajustadas
ℹ️  🏁 Mobilidade concluída!
ℹ️  🌐 Configurando conectividade de rede...
ℹ️  🔍 Testando conectividade entre dispositivos...
ℹ️  📈 Testando throughput da rede...
ℹ️  🛑 Finalizando simulação...
ℹ️  ✅ Simulação Rasp-Car Scanner concluída com sucesso!
============================================================
✅ Cenário executado com sucesso!
🎉 Execução concluída!
```

### 1. Executar Cenários (Método Manual)

```bash
# Configurar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.12/dist-packages:/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg

# Rasp-Car Scanner
sudo python3 scenarios/rasp_car_scan.py

# Rasp-Car-Rout (móvel)
sudo python3 scenarios/rasp_car_rout_scan.py
```

### 2. Analisar Logs
```bash
# Análise completa com gráficos
python3 tools/analyze_logs.py rasp_car_scan_log.csv

# Análise sem gráficos
python3 tools/analyze_logs.py rasp_car_rout_scan_log.csv --no-plots
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
- [x] 🌐 Interface web completa
- [x] Log em tempo real durante execução
- [x] Visualização de gráficos de mobilidade
- [x] Execução de cenários via interface web
- [x] Configuração sudoers para execução sem senha
- [x] 📊 **Progresso visual passo a passo** com emojis e contadores
- [x] 🔧 **Script wrapper** para execução simplificada
- [x] **Logs informativos** mostrando cada etapa da simulação
- [x] **Configuração automática** do PYTHONPATH
- [x] **Mensagens de erro claras** e ajuda integrada

### 🔄 Próximas Melhorias
- [ ] Simulação de obstáculos e paredes
- [ ] Modelo de interferência mais realista
- [ ] Handoff automático entre APs
- [ ] Mais cenários de teste
- [ ] Análise automática após execução

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

### Erro: "matplotlib not found"
```bash
# Instalar matplotlib
pip3 install matplotlib
```

### Interface Web não Inicia
```bash
# Verificar se a porta 5000 está livre
sudo lsof -i :5000
# Se necessário, matar processo
sudo kill -9 <PID>

# Ou usar porta diferente
python3 start_interface.py --port 5001
```

### Problemas com PYTHONPATH
```bash
# Usar o script wrapper (recomendado)
python3 run_scenario.py rasp-car

# Ou configurar manualmente
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.12/dist-packages:/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg
```

## 📝 Exemplos de Uso

### Interface Web (Recomendado)
```bash
# 1. Iniciar interface
python3 start_interface.py

# 2. Acessar no navegador
# http://localhost:5000

# 3. Clicar em "Executar" no cenário desejado
# 4. Acompanhar progresso e logs
# 5. Visualizar resultados
```

### Script Wrapper (Recomendado)
```bash
# Executar cenário com progresso visual
python3 run_scenario.py rasp-car

# Ver todos os cenários disponíveis
python3 run_scenario.py --help

# Executar cenário com modo verboso
python3 run_scenario.py rasp-car-rout -v

# 🎯 Executar Mastering Scenario 1
python3 run_scenario.py mastering-1
```

### Linha de Comando (Método Manual)
```bash
# Configurar ambiente
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.12/dist-packages:/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg

# Executar cenário básico
sudo python3 scenarios/basic_wifi.py

# Teste de interferência
sudo python3 scenarios/interference_test.py

# Análise comparativa
python3 tools/analyze_logs.py rasp_car_scan_log.csv
python3 tools/analyze_logs.py rasp_car_rout_scan_log.csv
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
**Versão**: 4.0 - Com progresso visual e script wrapper simplificado 