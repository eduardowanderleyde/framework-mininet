# Mininet-WiFi Framework

## 📡 Sobre o Projeto

Este projeto implementa uma rede Wi-Fi emulada usando Mininet-WiFi, que oferece:

- **Emulação realista de Wi-Fi** com stack real
- **Mobilidade de dispositivos** (Raspberry Pi simulados)
- **Interferência e perda de sinal** modeladas via wmediumd
- **Mudança dinâmica de AP** baseada em RSSI
- **Compatibilidade** com ferramentas padrão (iperf, ping, tcpdump)

## 🛠️ Instalação

### Pré-requisitos
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y git python3-pip build-essential libnl-3-dev libnl-genl-3-dev pkg-config libssl-dev ethtool
sudo apt install -y rfkill wireless-tools wpasupplicant hostapd
```

### Instalação do Mininet-WiFi
```bash
# Clonar Mininet-WiFi
git clone https://github.com/intrig-unicamp/mininet-wifi.git
cd mininet-wifi

# Instalar
sudo util/install.sh -Wlnfv

# Verificar instalação
sudo mn --wifi --test pingall
```

### Instalação do wmediumd (para interferência)
```bash
# Instalar wmediumd
sudo apt install -y wmediumd

# Ou compilar da fonte
git clone https://github.com/bcopeland/wmediumd.git
cd wmediumd
make
sudo make install
```

## 🚀 Uso Rápido

### Executar cenário básico
```bash
sudo python3 scenarios/basic_wifi_mobility.py
```

### Executar com mobilidade
```bash
sudo python3 scenarios/wifi_mesh_mobility.py
```

### Executar com interferência
```bash
sudo python3 scenarios/wifi_interference.py
```

## 📁 Estrutura do Projeto

```
framework-mininet/
├── scenarios/           # Cenários de teste
├── scripts/            # Scripts auxiliares
├── configs/            # Configurações
├── tools/              # Ferramentas de análise
└── docs/               # Documentação
```

## 🔧 Cenários Disponíveis

1. **basic_wifi_mobility.py** - Rede Wi-Fi básica com mobilidade
2. **wifi_mesh_mobility.py** - Rede mesh com dispositivos móveis
3. **wifi_interference.py** - Teste de interferência e RSSI
4. **sdn_wifi_test.py** - Validação de soluções SDN

## 📊 Monitoramento

### Verificar status da rede
```bash
# Listar nós
sudo mn --wifi --list

# Verificar conectividade
sudo mn --wifi --test pingall

# Monitorar tráfego
sudo tcpdump -i any -w capture.pcap
```

### Análise de performance
```bash
# Teste de throughput
sudo python3 tools/iperf_test.py

# Análise de RSSI
sudo python3 tools/rssi_monitor.py
```

## 🎯 Casos de Uso

### Validação de Redes Wi-Fi Mesh
- Teste de roteamento dinâmico
- Avaliação de throughput em diferentes topologias
- Análise de latência em redes mesh

### Testes com Mobilidade Controlada
- Simulação de dispositivos móveis
- Mudança automática de AP baseada em RSSI
- Análise de handoff performance

### Avaliação de Soluções SDN
- Controle centralizado de rede Wi-Fi
- Políticas de QoS dinâmicas
- Otimização de recursos de rede

## 🔍 Troubleshooting

### Problemas Comuns
1. **Erro de permissão**: Execute com `sudo`
2. **Interface não encontrada**: Verifique se `wmediumd` está rodando
3. **Dispositivo não conecta**: Verifique configurações de RSSI

### Logs e Debug
```bash
# Ver logs do Mininet-WiFi
sudo mn --wifi --log-level debug

# Verificar status do wmediumd
sudo systemctl status wmediumd
```

## 📚 Referências

- [Mininet-WiFi Documentation](https://github.com/intrig-unicamp/mininet-wifi)
- [wmediumd Documentation](https://github.com/bcopeland/wmediumd)
- [OpenFlow Protocol](https://opennetworking.org/software-defined-standards/specifications/)

## 🤝 Contribuição

Para contribuir com o projeto:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes. 

sudo bash scripts/install_mininet_wifi.sh 