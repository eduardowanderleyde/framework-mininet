#!/usr/bin/env python3
"""
Cenário de Teste de Interferência Wi-Fi
=======================================

Este script demonstra testes de interferência em redes Wi-Fi:
- Múltiplos APs em canais sobrepostos
- Análise de RSSI e interferência
- Simulação de ambientes ruidosos
- Avaliação de performance sob interferência

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
import math


def topology():
    """Cria a topologia para teste de interferência"""
    
    # Criar rede Mininet-WiFi
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       accessPoint=OVSKernelAP, enable_interference=True)
    
    info("*** Criando cenário de interferência Wi-Fi\n")
    
    # Adicionar controlador
    info("*** Adicionando controlador\n")
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
    
    # Adicionar APs com canais sobrepostos (causando interferência)
    info("*** Adicionando APs com interferência\n")
    
    # APs no canal 1 (interferência)
    ap1 = net.addAccessPoint('ap1', ssid='Rede1', mode='g', channel='1',
                            position='10,30,0', range=30)
    ap2 = net.addAccessPoint('ap2', ssid='Rede2', mode='g', channel='1',
                            position='50,30,0', range=30)
    
    # APs no canal 6 (interferência)
    ap3 = net.addAccessPoint('ap3', ssid='Rede3', mode='g', channel='6',
                            position='30,10,0', range=30)
    ap4 = net.addAccessPoint('ap4', ssid='Rede4', mode='g', channel='6',
                            position='70,50,0', range=30)
    
    # AP no canal 11 (sem interferência)
    ap5 = net.addAccessPoint('ap5', ssid='Rede5', mode='g', channel='11',
                            position='90,30,0', range=30)
    
    # Adicionar dispositivos de teste
    info("*** Adicionando dispositivos de teste\n")
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='15,25,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='55,25,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='35,15,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/24', position='75,45,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/24', position='95,25,0')
    
    # Configurar modelo de propagação com interferência
    info("*** Configurando modelo de propagação com interferência\n")
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    # Configurar wmediumd para interferência realista
    info("*** Configurando wmediumd para interferência\n")
    net.configureWifiNodes()
    
    # Construir rede
    info("*** Construindo rede\n")
    net.build()
    
    # Iniciar controlador
    info("*** Iniciando controlador\n")
    c0.start()
    
    # Iniciar APs
    info("*** Iniciando APs\n")
    for ap in [ap1, ap2, ap3, ap4, ap5]:
        ap.start([c0])
    
    # Função para calcular interferência
    def calculate_interference(sta, ap_list):
        """Calcula nível de interferência para um dispositivo"""
        total_interference = 0
        for ap in ap_list:
            distance = sta.getDistanceTo(ap)
            if distance > 0:
                # Modelo de interferência baseado em distância
                interference_power = 20 * math.log10(1 / distance)
                total_interference += interference_power
        return total_interference
    
    # Função para monitorar RSSI e interferência
    def monitor_interference():
        """Monitora RSSI e interferência em tempo real"""
        info("*** Monitorando RSSI e interferência\n")
        while True:
            for sta in [sta1, sta2, sta3, sta4, sta5]:
                info(f"\n--- {sta.name} ---\n")
                
                # Calcular RSSI para cada AP
                for ap in [ap1, ap2, ap3, ap4, ap5]:
                    distance = sta.getDistanceTo(ap)
                    if distance > 0:
                        # RSSI baseado em distância e potência de transmissão
                        rssi = -50 - (20 * math.log10(distance))
                        
                        # Adicionar interferência se no mesmo canal
                        interference_level = 0
                        if ap in [ap1, ap2] and ap != ap1:  # Canal 1
                            interference_level = calculate_interference(sta, [ap1, ap2])
                        elif ap in [ap3, ap4] and ap != ap3:  # Canal 6
                            interference_level = calculate_interference(sta, [ap3, ap4])
                        
                        final_rssi = rssi - interference_level
                        
                        status = "✓" if final_rssi > -70 else "✗"
                        info(f"{status} {ap.name} (Canal {ap.params['channel']}): "
                             f"RSSI={final_rssi:.1f} dBm, Dist={distance:.1f}m\n")
            
            time.sleep(10)
    
    # Iniciar thread de monitoramento
    interference_thread = threading.Thread(target=monitor_interference)
    interference_thread.daemon = True
    interference_thread.start()
    
    # Função para testar throughput sob interferência
    def test_interference_throughput():
        """Testa throughput sob diferentes condições de interferência"""
        info("*** Testando throughput sob interferência\n")
        while True:
            # Teste 1: Throughput sem interferência (canal 11)
            info("*** Teste 1: Throughput sem interferência (canal 11)\n")
            sta5.cmd('iperf -s -t 10 &')
            time.sleep(2)
            result1 = sta1.cmd('iperf -c 10.0.0.5 -t 8')
            info(f"Resultado canal 11: {result1}\n")
            
            time.sleep(5)
            
            # Teste 2: Throughput com interferência (canal 1)
            info("*** Teste 2: Throughput com interferência (canal 1)\n")
            sta1.cmd('iperf -s -t 10 &')
            time.sleep(2)
            result2 = sta2.cmd('iperf -c 10.0.0.1 -t 8')
            info(f"Resultado canal 1: {result2}\n")
            
            time.sleep(20)
    
    # Iniciar thread de teste de throughput
    throughput_thread = threading.Thread(target=test_interference_throughput)
    throughput_thread.daemon = True
    throughput_thread.start()
    
    # Função para simular movimento e mudança de canal
    def simulate_channel_hopping():
        """Simula mudança de canal para evitar interferência"""
        info("*** Simulando mudança de canal\n")
        while True:
            # Mover dispositivos para diferentes posições
            positions = [
                (15, 25),  # Próximo ao AP1 (canal 1)
                (55, 25),  # Próximo ao AP2 (canal 1)
                (35, 15),  # Próximo ao AP3 (canal 6)
                (75, 45),  # Próximo ao AP4 (canal 6)
                (95, 25),  # Próximo ao AP5 (canal 11)
            ]
            
            for i, sta in enumerate([sta1, sta2, sta3, sta4, sta5]):
                pos = positions[i]
                net.get(sta.name).setPosition(f'{pos[0]},{pos[1]},0')
                info(f"*** {sta.name} movido para posição {pos}\n")
            
            time.sleep(15)
    
    # Iniciar thread de mudança de canal
    hopping_thread = threading.Thread(target=simulate_channel_hopping)
    hopping_thread.daemon = True
    hopping_thread.start()
    
    # Aguardar estabilização
    info("*** Aguardando estabilização da rede\n")
    time.sleep(10)
    
    # Testar conectividade
    info("*** Testando conectividade\n")
    net.pingAll()
    
    # Mostrar informações da rede
    info("*** Informações da rede de interferência:\n")
    info("- AP1: Canal 1 (posição: 10,30) - Interferência com AP2\n")
    info("- AP2: Canal 1 (posição: 50,30) - Interferência com AP1\n")
    info("- AP3: Canal 6 (posição: 30,10) - Interferência com AP4\n")
    info("- AP4: Canal 6 (posição: 70,50) - Interferência com AP3\n")
    info("- AP5: Canal 11 (posição: 90,30) - Sem interferência\n")
    info("- STA1-5: Dispositivos de teste com monitoramento de RSSI\n")
    
    # Iniciar CLI interativa
    info("*** Iniciando CLI interativa\n")
    CLI_wifi(net)
    
    # Limpeza
    info("*** Parando rede de interferência\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology() 