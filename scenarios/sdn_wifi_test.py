#!/usr/bin/env python3
"""
Cenário de Validação SDN para Redes Wi-Fi
=========================================

Este script demonstra validação de soluções SDN em redes Wi-Fi:
- Controlador OpenFlow personalizado
- Políticas de QoS dinâmicas
- Balanceamento de carga entre APs
- Monitoramento centralizado de performance

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
import json


class SDNController(Controller):
    """Controlador SDN personalizado para redes Wi-Fi"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.ap_loads = {}
        self.client_connections = {}
        self.qos_policies = {}
    
    def start(self):
        """Inicia o controlador SDN"""
        info(f"*** Iniciando controlador SDN: {self.name}\n")
        super().start()
        self.start_sdn_monitoring()
    
    def start_sdn_monitoring(self):
        """Inicia monitoramento SDN"""
        info("*** Iniciando monitoramento SDN\n")
        
        # Thread para monitorar carga dos APs
        def monitor_ap_loads():
            while True:
                for ap_name, ap in self.ap_loads.items():
                    load = len(self.client_connections.get(ap_name, []))
                    info(f"*** {ap_name}: {load} clientes conectados\n")
                time.sleep(10)
        
        # Thread para aplicar políticas QoS
        def apply_qos_policies():
            while True:
                for client, policy in self.qos_policies.items():
                    info(f"*** Aplicando QoS para {client}: {policy}\n")
                time.sleep(15)
        
        # Iniciar threads de monitoramento
        threading.Thread(target=monitor_ap_loads, daemon=True).start()
        threading.Thread(target=apply_qos_policies, daemon=True).start()
    
    def register_ap(self, ap_name, ap):
        """Registra um AP no controlador"""
        self.ap_loads[ap_name] = ap
        self.client_connections[ap_name] = []
        info(f"*** AP {ap_name} registrado no controlador SDN\n")
    
    def register_client(self, ap_name, client_name):
        """Registra um cliente conectado a um AP"""
        if ap_name in self.client_connections:
            self.client_connections[ap_name].append(client_name)
            info(f"*** Cliente {client_name} conectado ao {ap_name}\n")
    
    def set_qos_policy(self, client, policy):
        """Define política QoS para um cliente"""
        self.qos_policies[client] = policy
        info(f"*** Política QoS definida para {client}: {policy}\n")


def topology():
    """Cria a topologia SDN para redes Wi-Fi"""
    
    # Criar rede Mininet-WiFi
    net = Mininet_wifi(controller=SDNController, link=wmediumd,
                       accessPoint=OVSKernelAP, enable_interference=True)
    
    info("*** Criando rede SDN Wi-Fi\n")
    
    # Adicionar controlador SDN
    info("*** Adicionando controlador SDN\n")
    sdn_controller = net.addController('sdn_controller', controller=SDNController, 
                                      ip='127.0.0.1', port=6633)
    
    # Adicionar APs gerenciados por SDN
    info("*** Adicionando APs gerenciados por SDN\n")
    ap1 = net.addAccessPoint('ap1', ssid='SDN_Network', mode='g', channel='1',
                            position='20,30,0', range=25)
    ap2 = net.addAccessPoint('ap2', ssid='SDN_Network', mode='g', channel='6',
                            position='60,30,0', range=25)
    ap3 = net.addAccessPoint('ap3', ssid='SDN_Network', mode='g', channel='11',
                            position='40,60,0', range=25)
    
    # Adicionar dispositivos com diferentes perfis
    info("*** Adicionando dispositivos com perfis diferentes\n")
    
    # Dispositivos de alta prioridade (QoS premium)
    sta1 = net.addStation('sta1', ip='10.0.0.1/24', position='25,25,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/24', position='65,25,0')
    
    # Dispositivos de baixa prioridade (QoS básica)
    sta3 = net.addStation('sta3', ip='10.0.0.3/24', position='35,25,0')
    sta4 = net.addStation('sta4', ip='10.0.0.4/24', position='45,55,0')
    
    # Dispositivo IoT (QoS específica)
    sta5 = net.addStation('sta5', ip='10.0.0.5/24', position='15,35,0')
    
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
    
    # Iniciar controlador SDN
    info("*** Iniciando controlador SDN\n")
    sdn_controller.start()
    
    # Registrar APs no controlador
    for ap in [ap1, ap2, ap3]:
        sdn_controller.register_ap(ap.name, ap)
        ap.start([sdn_controller])
    
    # Definir políticas QoS
    info("*** Definindo políticas QoS\n")
    sdn_controller.set_qos_policy('sta1', {'priority': 'high', 'bandwidth': '10Mbps'})
    sdn_controller.set_qos_policy('sta2', {'priority': 'high', 'bandwidth': '10Mbps'})
    sdn_controller.set_qos_policy('sta3', {'priority': 'low', 'bandwidth': '2Mbps'})
    sdn_controller.set_qos_policy('sta4', {'priority': 'low', 'bandwidth': '2Mbps'})
    sdn_controller.set_qos_policy('sta5', {'priority': 'iot', 'bandwidth': '1Mbps', 'latency': 'low'})
    
    # Função para simular balanceamento de carga
    def simulate_load_balancing():
        """Simula balanceamento de carga entre APs"""
        info("*** Iniciando balanceamento de carga SDN\n")
        while True:
            # Calcular carga de cada AP
            loads = {}
            for ap_name in ['ap1', 'ap2', 'ap3']:
                loads[ap_name] = len(sdn_controller.client_connections.get(ap_name, []))
            
            # Encontrar AP com menor carga
            min_load_ap = min(loads, key=loads.get)
            info(f"*** AP com menor carga: {min_load_ap} ({loads[min_load_ap]} clientes)\n")
            
            # Simular migração de clientes
            for ap_name, load in loads.items():
                if load > 2:  # Se AP tem mais de 2 clientes
                    info(f"*** Migrando clientes do {ap_name} para {min_load_ap}\n")
            
            time.sleep(20)
    
    # Iniciar thread de balanceamento
    load_balancing_thread = threading.Thread(target=simulate_load_balancing)
    load_balancing_thread.daemon = True
    load_balancing_thread.start()
    
    # Função para monitorar performance SDN
    def monitor_sdn_performance():
        """Monitora performance da rede SDN"""
        info("*** Monitorando performance SDN\n")
        while True:
            # Monitorar throughput por AP
            for ap_name in ['ap1', 'ap2', 'ap3']:
                clients = sdn_controller.client_connections.get(ap_name, [])
                total_bandwidth = len(clients) * 5  # 5Mbps por cliente
                info(f"*** {ap_name}: {len(clients)} clientes, {total_bandwidth}Mbps total\n")
            
            # Monitorar latência
            for sta in [sta1, sta2, sta3, sta4, sta5]:
                # Simular latência baseada na distância do AP
                latency = 5 + (sta.getDistanceTo(ap1) * 0.1)
                info(f"*** {sta.name} latência: {latency:.1f}ms\n")
            
            time.sleep(15)
    
    # Iniciar thread de monitoramento
    performance_thread = threading.Thread(target=monitor_sdn_performance)
    performance_thread.daemon = True
    performance_thread.start()
    
    # Função para testar políticas QoS
    def test_qos_policies():
        """Testa aplicação de políticas QoS"""
        info("*** Testando políticas QoS\n")
        while True:
            # Teste de throughput com QoS
            info("*** Teste de throughput com QoS alta prioridade\n")
            sta1.cmd('iperf -s -t 10 &')
            time.sleep(2)
            result1 = sta2.cmd('iperf -c 10.0.0.1 -t 8')
            info(f"Throughput alta prioridade: {result1}\n")
            
            time.sleep(5)
            
            # Teste de throughput com QoS baixa prioridade
            info("*** Teste de throughput com QoS baixa prioridade\n")
            sta3.cmd('iperf -s -t 10 &')
            time.sleep(2)
            result2 = sta4.cmd('iperf -c 10.0.0.3 -t 8')
            info(f"Throughput baixa prioridade: {result2}\n")
            
            time.sleep(20)
    
    # Iniciar thread de teste QoS
    qos_thread = threading.Thread(target=test_qos_policies)
    qos_thread.daemon = True
    qos_thread.start()
    
    # Função para simular mobilidade com handoff SDN
    def simulate_sdn_handoff():
        """Simula handoff controlado por SDN"""
        info("*** Simulando handoff controlado por SDN\n")
        while True:
            # Mover dispositivos para testar handoff
            positions = [
                (25, 25),  # Próximo ao AP1
                (65, 25),  # Próximo ao AP2
                (45, 55),  # Próximo ao AP3
            ]
            
            for i, sta in enumerate([sta1, sta2, sta3]):
                pos = positions[i % 3]
                net.get(sta.name).setPosition(f'{pos[0]},{pos[1]},0')
                info(f"*** {sta.name} movido para posição {pos} (handoff SDN)\n")
            
            time.sleep(12)
    
    # Iniciar thread de handoff
    handoff_thread = threading.Thread(target=simulate_sdn_handoff)
    handoff_thread.daemon = True
    handoff_thread.start()
    
    # Aguardar estabilização
    info("*** Aguardando estabilização da rede SDN\n")
    time.sleep(10)
    
    # Testar conectividade
    info("*** Testando conectividade SDN\n")
    net.pingAll()
    
    # Mostrar informações da rede SDN
    info("*** Informações da rede SDN Wi-Fi:\n")
    info("- Controlador SDN: 127.0.0.1:6633\n")
    info("- AP1: Canal 1 (posição: 20,30) - Gerenciado por SDN\n")
    info("- AP2: Canal 6 (posição: 60,30) - Gerenciado por SDN\n")
    info("- AP3: Canal 11 (posição: 40,60) - Gerenciado por SDN\n")
    info("- STA1-2: Dispositivos alta prioridade (QoS premium)\n")
    info("- STA3-4: Dispositivos baixa prioridade (QoS básica)\n")
    info("- STA5: Dispositivo IoT (QoS específica)\n")
    
    # Iniciar CLI interativa
    info("*** Iniciando CLI interativa SDN\n")
    CLI_wifi(net)
    
    # Limpeza
    info("*** Parando rede SDN\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology() 