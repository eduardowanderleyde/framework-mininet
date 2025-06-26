#!/usr/bin/env python3
"""
Cenário de Rede Wi-Fi Mesh com Mobilidade
=========================================

Este script demonstra uma rede mesh Wi-Fi com:
- Múltiplos nós mesh (Raspberry Pi simulados)
- Roteamento dinâmico baseado em RSSI
- Mobilidade controlada com handoff automático
- Análise de throughput em diferentes topologias

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
import random


def topology():
    """Cria a topologia da rede mesh Wi-Fi"""
    
    # Criar rede Mininet-WiFi
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       accessPoint=OVSKernelAP, enable_interference=True)
    
    info("*** Criando rede mesh Wi-Fi\n")
    
    # Adicionar controlador
    info("*** Adicionando controlador\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
    
    # Adicionar nós mesh (APs que também são clientes)
    info("*** Adicionando nós mesh\n")
    mesh1 = net.addAccessPoint('mesh1', ssid='MeshNetwork', mode='g', channel='1',
                              position='10,10,0', range=25, inNamespace=False)
    mesh2 = net.addAccessPoint('mesh2', ssid='MeshNetwork', mode='g', channel='1',
                              position='40,10,0', range=25, inNamespace=False)
    mesh3 = net.addAccessPoint('mesh3', ssid='MeshNetwork', mode='g', channel='1',
                              position='70,10,0', range=25, inNamespace=False)
    mesh4 = net.addAccessPoint('mesh4', ssid='MeshNetwork', mode='g', channel='1',
                              position='25,40,0', range=25, inNamespace=False)
    mesh5 = net.addAccessPoint('mesh5', ssid='MeshNetwork', mode='g', channel='1',
                              position='55,40,0', range=25, inNamespace=False)
    
    # Adicionar dispositivos móveis
    info("*** Adicionando dispositivos móveis\n")
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='15,15,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='45,15,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='75,15,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/24', position='30,45,0')
    
    # Configurar modelo de propagação
    info("*** Configurando modelo de propagação\n")
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    # Configurar mobilidade
    info("*** Configurando mobilidade\n")
    net.setMobilityModel(time=0, model='RandomWayPoint', max_x=100, max_y=100)
    
    # Configurar wmediumd
    info("*** Configurando wmediumd\n")
    net.configureWifiNodes()
    
    # Construir rede
    info("*** Construindo rede\n")
    net.build()
    
    # Iniciar controlador
    info("*** Iniciando controlador\n")
    c0.start()
    
    # Iniciar nós mesh
    info("*** Iniciando nós mesh\n")
    for mesh in [mesh1, mesh2, mesh3, mesh4, mesh5]:
        mesh.start([c0])
    
    # Função para simular mobilidade complexa
    def simulate_mesh_mobility():
        """Simula movimento complexo na rede mesh"""
        info("*** Iniciando simulação de mobilidade mesh\n")
        
        # Pontos de interesse na rede mesh
        mesh_points = [
            (15, 15),  # Próximo ao mesh1
            (45, 15),  # Próximo ao mesh2
            (75, 15),  # Próximo ao mesh3
            (30, 45),  # Próximo ao mesh4
            (55, 45),  # Próximo ao mesh5
            (40, 25),  # Centro da rede
        ]
        
        for i in range(20):
            # Mover dispositivos para pontos aleatórios
            for sta in [sta1, sta2, sta3, sta4]:
                point = random.choice(mesh_points)
                net.get(sta.name).setPosition(f'{point[0]},{point[1]},0')
                info(f"*** {sta.name} movido para posição {point}\n")
            
            time.sleep(8)
    
    # Iniciar thread de mobilidade
    mobility_thread = threading.Thread(target=simulate_mesh_mobility)
    mobility_thread.daemon = True
    mobility_thread.start()
    
    # Função para monitorar conectividade mesh
    def monitor_mesh_connectivity():
        """Monitora conectividade da rede mesh"""
        info("*** Monitorando conectividade mesh\n")
        while True:
            for sta in [sta1, sta2, sta3, sta4]:
                for mesh in [mesh1, mesh2, mesh3, mesh4, mesh5]:
                    distance = sta.getDistanceTo(mesh)
                    rssi = -50 - (distance * 2)  # Simulação de RSSI
                    if rssi > -70:  # Threshold de conectividade
                        info(f"✓ {sta.name} conectado ao {mesh.name} (RSSI: {rssi:.1f} dBm)\n")
                    else:
                        info(f"✗ {sta.name} desconectado do {mesh.name} (RSSI: {rssi:.1f} dBm)\n")
            time.sleep(15)
    
    # Iniciar thread de monitoramento
    connectivity_thread = threading.Thread(target=monitor_mesh_connectivity)
    connectivity_thread.daemon = True
    connectivity_thread.start()
    
    # Função para testar throughput
    def test_mesh_throughput():
        """Testa throughput entre nós da rede mesh"""
        info("*** Testando throughput da rede mesh\n")
        while True:
            # Teste de throughput entre sta1 e sta3
            info("*** Iniciando teste de throughput sta1 -> sta3\n")
            sta1.cmd('iperf -s -t 10 &')
            time.sleep(2)
            result = sta3.cmd('iperf -c 10.0.0.1 -t 8')
            info(f"Resultado throughput: {result}\n")
            time.sleep(20)
    
    # Iniciar thread de teste de throughput
    throughput_thread = threading.Thread(target=test_mesh_throughput)
    throughput_thread.daemon = True
    throughput_thread.start()
    
    # Aguardar estabilização
    info("*** Aguardando estabilização da rede mesh\n")
    time.sleep(10)
    
    # Testar conectividade
    info("*** Testando conectividade da rede mesh\n")
    net.pingAll()
    
    # Mostrar informações da rede mesh
    info("*** Informações da rede mesh:\n")
    info("- Mesh1: 10.0.0.10 (posição: 10,10)\n")
    info("- Mesh2: 10.0.0.11 (posição: 40,10)\n")
    info("- Mesh3: 10.0.0.12 (posição: 70,10)\n")
    info("- Mesh4: 10.0.0.13 (posição: 25,40)\n")
    info("- Mesh5: 10.0.0.14 (posição: 55,40)\n")
    info("- STA1-4: Dispositivos móveis com roteamento dinâmico\n")
    
    # Iniciar CLI interativa
    info("*** Iniciando CLI interativa\n")
    CLI_wifi(net)
    
    # Limpeza
    info("*** Parando rede mesh\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology() 