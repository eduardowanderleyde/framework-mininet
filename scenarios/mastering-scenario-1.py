#!/usr/bin/env python3
"""
🎯 Mastering Scenario 1: Ambiente Vazio com 3 Roteadores Mesh + Raspberry Pi Móvel

Cenário: Simulação de rede mesh Wi-Fi em ambiente aberto
- 3 roteadores mesh conectados entre si
- 1 roteador principal conectado à internet
- 1 roteador fixo como repetidor
- 1 roteador móvel em carrinho + Raspberry Pi scanner

Autor: Eduardo Wanderley
Data: Dezembro 2024
"""

import time
import csv
import threading
import subprocess
import os
from datetime import datetime
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class MeshCartScenario:
    def __init__(self):
        self.net = None
        self.log_file = None
        self.scanning_active = True
        self.mobility_active = True
        self.scan_thread = None
        self.mobility_thread = None
        
    def create_network(self):
        """Cria a rede mesh com 3 roteadores e Raspberry Pi móvel"""
        info("🎯 Criando rede mesh Wi-Fi...\n")
        
        # Configurar rede Mininet-WiFi
        self.net = Mininet_wifi(
            controller=Controller,
            link=wmediumd,
            accessPoint=OVSKernelAP,
            enable_interference=False,
            noise_threshold=-91,
            fading_coefficient=0
        )
        
        # Configurar modelo de propagação para ambiente aberto
        self.net.setPropagationModel(model="logDistance", exp=2.5)
        
        # Adicionar controlador
        info("🔌 Configurando controlador...\n")
        c0 = self.net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
        
        # 🔌 Roteador 1 (Mesh + Backbone) - Conectado à internet
        info("🔌 Configurando roteador principal (backbone)...\n")
        router1 = self.net.addAccessPoint(
            'router1', 
            ssid='Mesh-Backbone',
            mode='g',
            channel='1',
            position='0,0,0',
            range=80,  # Range maior para ambiente aberto
            protocols='OpenFlow13'
        )
        
        # 📡 Roteador 2 (Mesh Repetidor Fixo)
        info("📡 Configurando roteador repetidor fixo...\n")
        router2 = self.net.addAccessPoint(
            'router2',
            ssid='Mesh-Repeater',
            mode='g', 
            channel='6',
            position='50,50,0',
            range=80,
            protocols='OpenFlow13'
        )
        
        # 🚗 Roteador 3 (Mesh Móvel em Carrinho)
        info("🚗 Configurando roteador móvel (carrinho)...\n")
        router3 = self.net.addAccessPoint(
            'router3',
            ssid='Mesh-Mobile',
            mode='g',
            channel='11', 
            position='25,25,0',
            range=80,
            protocols='OpenFlow13'
        )
        
        # 📱 Raspberry Pi (Scanner no Carrinho)
        info("📱 Configurando Raspberry Pi scanner...\n")
        raspberry = self.net.addStation(
            'raspberry',
            ip='192.168.1.100/24',
            position='25,25,0',
            range=50
        )
        
        # Configurar conectividade mesh entre roteadores
        info("🌐 Configurando conectividade mesh...\n")
        self.net.addLink(router1, router2)  # Mesh link 1-2
        self.net.addLink(router1, router3)  # Mesh link 1-3  
        self.net.addLink(router2, router3)  # Mesh link 2-3
        
        # Conectar Raspberry Pi ao roteador móvel
        self.net.addLink(raspberry, router3)
        
        # Configurar roteamento
        self.net.setMobilityModel(time=0, model='RandomDirection', max_x=100, max_y=100)
        
        info("✅ Rede mesh criada com sucesso!\n")
        
    def setup_logging(self):
        """Configura sistema de logging CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/mastering_scenario_1_log_{timestamp}.csv"
        
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
        
        # Criar arquivo CSV com cabeçalhos
        with open(self.log_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp', 'raspberry_x', 'raspberry_y', 'raspberry_z',
                'router3_x', 'router3_y', 'router3_z', 'best_ap', 'ssid',
                'rssi', 'distance_to_ap', 'latency_ms', 'throughput_mbps',
                'packet_loss_percent', 'handover_detected', 'mesh_connected'
            ])
        
        info(f"📊 Log configurado: {self.log_file}\n")
        
    def calculate_distance(self, x1, y1, z1, x2, y2, z2):
        """Calcula distância entre dois pontos"""
        return ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5
        
    def get_rssi(self, distance, tx_power=-20):
        """Calcula RSSI baseado na distância (modelo log-distance)"""
        if distance <= 1:
            return tx_power
        else:
            # Modelo log-distance com expoente 2.5 para ambiente aberto
            path_loss = 20 * 2.5 * (distance / 1)
            return tx_power - path_loss
            
    def measure_latency(self, host, target_ip):
        """Mede latência via ping"""
        try:
            result = host.cmd(f'ping -c 1 -W 1 {target_ip}')
            if 'time=' in result:
                latency = float(result.split('time=')[1].split()[0])
                return latency
            else:
                return 999.0  # Timeout
        except:
            return 999.0
            
    def measure_throughput(self, host, target_ip):
        """Mede throughput via iperf"""
        try:
            # Iniciar servidor iperf em background
            server_cmd = f'iperf -s -t 2 -i 1'
            server_result = host.cmd(server_cmd)
            
            # Cliente iperf
            client_cmd = f'iperf -c {target_ip} -t 2 -i 1'
            client_result = host.cmd(client_cmd)
            
            if 'Mbits/sec' in client_result:
                throughput = float(client_result.split('Mbits/sec')[0].split()[-1])
                return throughput
            else:
                return 0.0
        except:
            return 0.0
            
    def scan_network(self):
        """Thread de escaneamento contínuo da rede"""
        info("🔍 Iniciando sistema de escaneamento...\n")
        
        raspberry = self.net.get('raspberry')
        router1 = self.net.get('router1')
        router2 = self.net.get('router2') 
        router3 = self.net.get('router3')
        
        cycle = 0
        last_ap = None
        
        while self.scanning_active:
            try:
                cycle += 1
                info(f"🔄 [Ciclo {cycle}] Escaneando rede...\n")
                
                # Obter posição atual do Raspberry Pi
                pos = raspberry.params['position']
                rasp_x, rasp_y, rasp_z = map(float, pos.split(','))
                
                # Obter posição do roteador móvel (carrinho)
                router3_pos = router3.params['position']
                router3_x, router3_y, router3_z = map(float, router3_pos.split(','))
                
                # Calcular distâncias para cada AP
                dist_to_router1 = self.calculate_distance(rasp_x, rasp_y, rasp_z, 0, 0, 0)
                dist_to_router2 = self.calculate_distance(rasp_x, rasp_y, rasp_z, 50, 50, 0)
                dist_to_router3 = self.calculate_distance(rasp_x, rasp_y, rasp_z, router3_x, router3_y, router3_z)
                
                # Calcular RSSI para cada AP
                rssi_router1 = self.get_rssi(dist_to_router1)
                rssi_router2 = self.get_rssi(dist_to_router2)
                rssi_router3 = self.get_rssi(dist_to_router3)
                
                # Determinar melhor AP baseado no RSSI
                ap_rssi_map = {
                    'router1': (rssi_router1, dist_to_router1, 'Mesh-Backbone'),
                    'router2': (rssi_router2, dist_to_router2, 'Mesh-Repeater'),
                    'router3': (rssi_router3, dist_to_router3, 'Mesh-Mobile')
                }
                
                best_ap = max(ap_rssi_map.keys(), key=lambda k: ap_rssi_map[k][0])
                best_rssi, best_distance, best_ssid = ap_rssi_map[best_ap]
                
                # Detectar handover
                handover_detected = "YES" if last_ap and last_ap != best_ap else "NO"
                last_ap = best_ap
                
                # Medir latência para o roteador principal
                latency = self.measure_latency(raspberry, '192.168.1.1')
                
                # Medir throughput
                throughput = self.measure_throughput(raspberry, '192.168.1.1')
                
                # Simular perda de pacotes baseada na distância
                packet_loss = min(100, max(0, (best_distance / 100) * 20))
                
                # Verificar conectividade mesh
                mesh_connected = "YES" if best_rssi > -70 else "NO"
                
                # Log dos dados
                timestamp = time.time()
                log_data = [
                    timestamp, rasp_x, rasp_y, rasp_z,
                    router3_x, router3_y, router3_z, best_ap, best_ssid,
                    round(best_rssi, 2), round(best_distance, 2), 
                    round(latency, 2), round(throughput, 2),
                    round(packet_loss, 2), handover_detected, mesh_connected
                ]
                
                # Salvar no CSV
                with open(self.log_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(log_data)
                
                # Exibir informações em tempo real
                info(f"📍 Posição Raspberry: ({rasp_x:.1f}, {rasp_y:.1f}, {rasp_z:.1f})\n")
                info(f"🚗 Posição Carrinho: ({router3_x:.1f}, {router3_y:.1f}, {router3_z:.1f})\n")
                info(f"📶 Melhor AP: {best_ap} ({best_ssid})\n")
                info(f"📊 RSSI: {best_rssi:.2f} dBm | Distância: {best_distance:.2f}m\n")
                info(f"⏱️  Latência: {latency:.2f}ms | Throughput: {throughput:.2f} Mbps\n")
                info(f"📦 Perda: {packet_loss:.2f}% | Handover: {handover_detected}\n")
                info(f"🌐 Mesh: {mesh_connected}\n")
                info("─" * 60 + "\n")
                
                time.sleep(2)  # Escaneamento a cada 2 segundos
                
            except Exception as e:
                info(f"❌ Erro no escaneamento: {e}\n")
                time.sleep(1)
                
        info("✅ Sistema de escaneamento finalizado!\n")
        
    def move_cart(self):
        """Thread de mobilidade do carrinho com roteador e Raspberry Pi"""
        info("🚗 Iniciando mobilidade do carrinho...\n")
        
        router3 = self.net.get('router3')
        raspberry = self.net.get('raspberry')
        
        # Pontos de interesse para testar conectividade
        # Roteador 1 (backbone) em (0,0)
        # Roteador 2 (repetidor) em (50,50)
        # O carrinho vai circular entre esses pontos para testar a qualidade
        
        waypoints = [
            (0, 0, 0),      # Próximo ao roteador backbone
            (25, 0, 0),     # Meio caminho entre backbone e repetidor
            (50, 50, 0),    # Próximo ao roteador repetidor
            (25, 50, 0),    # Meio caminho de volta
            (0, 25, 0),     # Outro ponto intermediário
            (25, 25, 0),    # Centro da área
        ]
        
        current_waypoint = 0
        waypoint_radius = 5  # Distância de aproximação dos roteadores
        
        while self.mobility_active:
            try:
                # Obter waypoint atual
                target_x, target_y, target_z = waypoints[current_waypoint]
                
                # Obter posição atual do carrinho
                current_pos = router3.params['position']
                current_x, current_y, current_z = map(float, current_pos.split(','))
                
                # Calcular distância até o waypoint
                distance_to_target = self.calculate_distance(current_x, current_y, current_z, target_x, target_y, target_z)
                
                # Se chegou próximo ao waypoint, ir para o próximo
                if distance_to_target < waypoint_radius:
                    current_waypoint = (current_waypoint + 1) % len(waypoints)
                    target_x, target_y, target_z = waypoints[current_waypoint]
                    info(f"🎯 Waypoint alcançado! Indo para próximo ponto: ({target_x}, {target_y})\n")
                
                # Calcular nova posição (movimento suave em direção ao waypoint)
                step_size = 2.0  # Metros por movimento
                
                # Calcular direção
                dx = target_x - current_x
                dy = target_y - current_y
                dz = target_z - current_z
                
                # Normalizar e aplicar step
                distance = (dx**2 + dy**2 + dz**2)**0.5
                if distance > 0:
                    dx = (dx / distance) * step_size
                    dy = (dy / distance) * step_size
                    dz = (dz / distance) * step_size
                
                # Nova posição
                new_x = current_x + dx
                new_y = current_y + dy
                new_z = current_z + dz
                
                # Mover roteador móvel (carrinho)
                router3.setPosition(f'{new_x},{new_y},{new_z}')
                
                # Mover Raspberry Pi junto com o carrinho
                raspberry.setPosition(f'{new_x},{new_y},{new_z}')
                
                # Identificar qual roteador está mais próximo
                dist_to_router1 = self.calculate_distance(new_x, new_y, new_z, 0, 0, 0)
                dist_to_router2 = self.calculate_distance(new_x, new_y, new_z, 50, 50, 0)
                
                closest_router = "router1" if dist_to_router1 < dist_to_router2 else "router2"
                closest_distance = min(dist_to_router1, dist_to_router2)
                
                info(f"🚗 Carrinho movido para: ({new_x:.1f}, {new_y:.1f}, {new_z:.1f})\n")
                info(f"🎯 Próximo ao: {closest_router} (distância: {closest_distance:.1f}m)\n")
                info(f"📍 Waypoint atual: {current_waypoint + 1}/{len(waypoints)}\n")
                info("─" * 40 + "\n")
                
                time.sleep(2)  # Movimento a cada 2 segundos
                
            except Exception as e:
                info(f"❌ Erro na mobilidade: {e}\n")
                time.sleep(1)
                
        info("✅ Mobilidade do carrinho finalizada!\n")
        
    def run_simulation(self, duration=60):
        """Executa a simulação completa"""
        info("🎯 Iniciando Mastering Scenario 1...\n")
        info("=" * 60 + "\n")
        
        try:
            # Criar rede
            self.create_network()
            
            # Configurar logging
            self.setup_logging()
            
            # Construir e iniciar rede
            info("🔨 Construindo rede...\n")
            self.net.build()
            
            info("🎮 Iniciando controlador...\n")
            for controller in self.net.controllers:
                controller.start()
                
            info("📶 Ativando access points...\n")
            for ap in self.net.accessPoints:
                ap.start([self.net.controllers[0]])
                
            info("✅ Rede Wi-Fi mesh ativada com sucesso!\n")
            
            # Aguardar estabilização
            time.sleep(3)
            
            # Iniciar threads de escaneamento e mobilidade
            info("🔄 Iniciando threads de mobilidade e escaneamento...\n")
            self.scan_thread = threading.Thread(target=self.scan_network)
            self.mobility_thread = threading.Thread(target=self.move_cart)
            
            self.scan_thread.start()
            self.mobility_thread.start()
            
            # Executar simulação por tempo determinado
            info(f"⏱️  Executando simulação por {duration} segundos...\n")
            time.sleep(duration)
            
            # Finalizar threads
            info("🛑 Finalizando threads...\n")
            self.scanning_active = False
            self.mobility_active = False
            
            # Aguardar threads terminarem
            if self.scan_thread:
                self.scan_thread.join()
            if self.mobility_thread:
                self.mobility_thread.join()
                
            # Configurar conectividade de rede
            info("🌐 Configurando conectividade de rede...\n")
            self.net.configureWifiNodes()
            
            # Testar conectividade
            info("🔍 Testando conectividade entre dispositivos...\n")
            self.net.pingAll()
            
            # Testar throughput
            info("📈 Testando throughput da rede...\n")
            self.net.iperf()
            
            info("✅ Simulação Mastering Scenario 1 concluída com sucesso!\n")
            info(f"📊 Logs salvos em: {self.log_file}\n")
            
            # Ajustar permissões do arquivo de log
            if self.log_file and os.path.exists(self.log_file):
                os.chmod(self.log_file, 0o666)
                info("🔐 Permissões do arquivo ajustadas\n")
                
        except Exception as e:
            info(f"❌ Erro na simulação: {e}\n")
            raise
        finally:
            # Limpar recursos
            if self.net:
                self.net.stop()
                
def main():
    """Função principal"""
    setLogLevel('info')
    
    # Criar e executar cenário
    scenario = MeshCartScenario()
    
    try:
        # Executar simulação por 60 segundos
        scenario.run_simulation(duration=60)
        
        # Manter CLI aberto para análise manual
        info("🎮 Abrindo CLI para análise manual...\n")
        info("💡 Comandos úteis:\n")
        info("   - nodes: Listar todos os nós\n")
        info("   - links: Listar todas as conexões\n")
        info("   - dump: Ver informações detalhadas\n")
        info("   - pingall: Testar conectividade\n")
        info("   - iperf: Testar throughput\n")
        info("   - exit: Sair\n")
        
        CLI(scenario.net)
        
    except KeyboardInterrupt:
        info("\n🛑 Simulação interrompida pelo usuário\n")
    except Exception as e:
        info(f"❌ Erro: {e}\n")
    finally:
        if scenario.net:
            scenario.net.stop()

if __name__ == '__main__':
    main() 