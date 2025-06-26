#!/usr/bin/env python3
"""
Cenário Básico de Wi-Fi com Mobilidade
======================================

Este script demonstra uma rede Wi-Fi básica com:
- 2 Access Points (APs)
- 3 dispositivos móveis (Raspberry Pi simulados)
- Mobilidade controlada baseada em RSSI
- Mudança automática de AP

Autor: Framework Mininet-WiFi
Data: 2024
"""

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mininet.wifi.node import OVSKernelAP
from mininet.wifi.link import wmediumd, _4address
from mininet.wifi.cli import CLI_wifi
from mininet.wifi.net import Mininet_wifi
from mininet.wifi.wmediumdConnector import interference
import time
import threading


def topology():
    """Cria a topologia da rede Wi-Fi com mobilidade"""
    
    # Criar rede Mininet-WiFi
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       accessPoint=OVSKernelAP, enable_interference=True)
    
    info("*** Criando nós da rede\n")
    
    # Adicionar controlador
    info("*** Adicionando controlador\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
    
    # Adicionar Access Points
    info("*** Adicionando Access Points\n")
    ap1 = net.addAccessPoint('ap1', ssid='RedeWiFi1', mode='g', channel='1',
                            position='10,30,0', range=20)
    ap2 = net.addAccessPoint('ap2', ssid='RedeWiFi2', mode='g', channel='6',
                            position='60,30,0', range=20)
    
    # Adicionar dispositivos móveis (Raspberry Pi simulados)
    info("*** Adicionando dispositivos móveis\n")
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='15,25,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='55,25,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='35,25,0')
    
    # Configurar interferência
    info("*** Configurando interferência\n")
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    # Configurar mobilidade
    info("*** Configurando mobilidade\n")
    net.setMobilityModel(time=0, model='RandomDirection', max_x=100, max_y=100)
    
    # Configurar wmediumd para interferência realista
    info("*** Configurando wmediumd\n")
    net.configureWifiNodes()
    
    # Construir rede
    info("*** Construindo rede\n")
    net.build()
    
    # Iniciar controlador
    info("*** Iniciando controlador\n")
    c0.start()
    
    # Iniciar Access Points
    info("*** Iniciando Access Points\n")
    net.get('ap1').start([c0])
    net.get('ap2').start([c0])
    
    # Função para simular mobilidade
    def simulate_mobility():
        """Simula movimento dos dispositivos móveis"""
        info("*** Iniciando simulação de mobilidade\n")
        
        # Movimento do sta1 entre APs
        for i in range(10):
            # Mover sta1 para próximo do AP1
            net.get('sta1').setPosition('15,25,0')
            time.sleep(5)
            
            # Mover sta1 para próximo do AP2
            net.get('sta1').setPosition('55,25,0')
            time.sleep(5)
            
            # Mover sta1 para posição intermediária
            net.get('sta1').setPosition('35,25,0')
            time.sleep(5)
    
    # Iniciar thread de mobilidade
    mobility_thread = threading.Thread(target=simulate_mobility)
    mobility_thread.daemon = True
    mobility_thread.start()
    
    # Função para monitorar RSSI
    def monitor_rssi():
        """Monitora RSSI dos dispositivos"""
        info("*** Monitorando RSSI\n")
        while True:
            for sta in [sta1, sta2, sta3]:
                for ap in [ap1, ap2]:
                    rssi = sta.getDistanceTo(ap)
                    info(f"RSSI {sta.name} -> {ap.name}: {rssi:.2f} dBm\n")
            time.sleep(10)
    
    # Iniciar thread de monitoramento
    rssi_thread = threading.Thread(target=monitor_rssi)
    rssi_thread.daemon = True
    rssi_thread.start()
    
    # Aguardar estabilização da rede
    info("*** Aguardando estabilização da rede\n")
    time.sleep(5)
    
    # Testar conectividade
    info("*** Testando conectividade\n")
    net.pingAll()
    
    # Mostrar informações da rede
    info("*** Informações da rede:\n")
    info("- AP1: 10.0.0.10 (posição: 10,30)\n")
    info("- AP2: 10.0.0.11 (posição: 60,30)\n")
    info("- STA1: 10.0.0.1 (móvel)\n")
    info("- STA2: 10.0.0.2 (móvel)\n")
    info("- STA3: 10.0.0.3 (móvel)\n")
    
    # Iniciar CLI interativa
    info("*** Iniciando CLI interativa\n")
    CLI_wifi(net)
    
    # Limpeza
    info("*** Parando rede\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology() 