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
import math
import os
from datetime import datetime
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi

def print_progress(message, step=None, total=None):
    """Função para imprimir progresso de forma clara"""
    if step and total:
        progress = (step / total) * 100
        info(f"🔄 [{progress:.0f}%] {message}\n")
    else:
        info(f"ℹ️  {message}\n")

def topology():
    print_progress("🎯 Iniciando Mastering Scenario 1...")
    print_progress("=" * 60)
    
    # Configurar rede Mininet-WiFi
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    
    print_progress("🔌 Configurando controlador...")
    c0 = net.addController('c0', controller=Controller)
    
    # 🔌 Roteador 1 (Mesh + Backbone) - Conectado à internet
    print_progress("🔌 Configurando roteador principal (backbone)...")
    router1 = net.addAccessPoint(
        'router1', 
        ssid='Mesh-Backbone',
        mode='g',
        channel='1',
        position='0,0,0',
        range=80,
        dpid='1'
    )
    
    # 📡 Roteador 2 (Mesh Repetidor Fixo)
    print_progress("📡 Configurando roteador repetidor fixo...")
    router2 = net.addAccessPoint(
        'router2',
        ssid='Mesh-Repeater',
        mode='g', 
        channel='6',
        position='50,50,0',
        range=80,
        dpid='2'
    )
    
    # 🚗 Roteador 3 (Mesh Móvel em Carrinho)
    print_progress("🚗 Configurando roteador móvel (carrinho)...")
    router3 = net.addAccessPoint(
        'router3',
        ssid='Mesh-Mobile',
        mode='g',
        channel='11', 
        position='25,25,0',
        range=80,
        dpid='3'
    )
    
    # 📱 Raspberry Pi (Scanner no Carrinho)
    print_progress("📱 Configurando Raspberry Pi scanner...")
    raspberry = net.addStation(
        'raspberry',
        ip='192.168.1.100/24',
        position='25,25,0'
    )
    
    print_progress("⚙️  Configurando modelo de propagação...")
    net.setPropagationModel(model="logDistance", exp=2.5)
    net.configureWifiNodes()
    
    print_progress("🔨 Construindo rede...")
    net.build()
    
    print_progress("🎮 Iniciando controlador...")
    c0.start()
    
    print_progress("📶 Ativando access points...")
    router1.start([c0])
    router2.start([c0])
    router3.start([c0])
    
    print_progress("✅ Rede Wi-Fi mesh ativada com sucesso!")
    
    # Configurar IPs dos roteadores
    router1.cmd('ifconfig router1-wlan1 192.168.1.1/24')
    router2.cmd('ifconfig router2-wlan1 192.168.1.2/24')
    router3.cmd('ifconfig router3-wlan1 192.168.1.3/24')
    
    # Configurar roteamento
    raspberry.cmd('route add default gw 192.168.1.1')
    
    # Função de escaneamento e log em CSV
    def scan_and_log():
        print_progress("📊 Iniciando sistema de escaneamento e log...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f'logs/mastering_scenario_1_log_{timestamp}.csv'
        
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
        
        with open(log_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'raspberry_x', 'raspberry_y', 'raspberry_z',
                'router3_x', 'router3_y', 'router3_z', 'best_ap', 'ssid',
                'rssi', 'distance_to_ap', 'latency_ms', 'throughput_mbps',
                'packet_loss_percent', 'handover_detected', 'mesh_connected'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total_scans = 30  # Mais scans para melhor análise
            last_ap = None
            
            for i in range(total_scans):
                print_progress(f"🔍 Escaneando rede (ciclo {i+1}/{total_scans})...", i+1, total_scans)
                
                # Obter posição atual do Raspberry Pi
                try:
                    rasp_x = float(raspberry.params.get('x', 25))
                    rasp_y = float(raspberry.params.get('y', 25))
                    rasp_z = float(raspberry.params.get('z', 0))
                except:
                    rasp_x, rasp_y, rasp_z = 25, 25, 0
                
                # Obter posição do roteador móvel (carrinho)
                try:
                    router3_x = float(router3.params.get('x', 25))
                    router3_y = float(router3.params.get('y', 25))
                    router3_z = float(router3.params.get('z', 0))
                except:
                    router3_x, router3_y, router3_z = 25, 25, 0
                
                best_ap = None
                best_rssi = -999
                best_distance = 999
                best_ssid = ""
                
                # Testar cada AP
                aps = [
                    (router1, 'Mesh-Backbone', 0, 0, 0),
                    (router2, 'Mesh-Repeater', 50, 50, 0),
                    (router3, 'Mesh-Mobile', router3_x, router3_y, router3_z)
                ]
                
                for ap, ssid, ap_x, ap_y, ap_z in aps:
                    try:
                        # Calcular distância
                        distance = math.sqrt((rasp_x - ap_x)**2 + (rasp_y - ap_y)**2 + (rasp_z - ap_z)**2)
                        if distance < 0.01:
                            distance = 0.01
                        
                        # Calcular RSSI realista
                        tx_power = 20  # dBm
                        freq = 2.4e9   # 2.4 GHz
                        c = 3e8        # velocidade da luz
                        fspl = 20 * math.log10(distance) + 20 * math.log10(freq) + 20 * math.log10(4 * math.pi / c)
                        additional_losses = 5  # dB (ambiente aberto)
                        rssi = tx_power - fspl - additional_losses
                        
                        if rssi > best_rssi:
                            best_rssi = rssi
                            best_ap = ap.name
                            best_distance = distance
                            best_ssid = ssid
                    except Exception as e:
                        info(f"⚠️  Erro ao calcular RSSI para {ap.name}: {e}\n")
                        continue
                
                # Detectar handover
                handover_detected = "YES" if last_ap and last_ap != best_ap else "NO"
                last_ap = best_ap
                
                # Calcular latência simulada
                latency = 5 + (best_distance * 0.1) if best_distance < 999 else 999
                
                # Simular throughput baseado no RSSI
                if best_rssi > -50:
                    throughput = 54.0  # Máximo 802.11g
                elif best_rssi > -60:
                    throughput = 36.0
                elif best_rssi > -70:
                    throughput = 18.0
                else:
                    throughput = 6.0
                
                # Simular perda de pacotes baseada na distância
                packet_loss = min(100, max(0, (best_distance / 100) * 15))
                
                # Verificar conectividade mesh
                mesh_connected = "YES" if best_rssi > -70 else "NO"
                
                if best_ap:
                    writer.writerow({
                        'timestamp': time.time(),
                        'raspberry_x': round(rasp_x, 2),
                        'raspberry_y': round(rasp_y, 2),
                        'raspberry_z': round(rasp_z, 2),
                        'router3_x': round(router3_x, 2),
                        'router3_y': round(router3_y, 2),
                        'router3_z': round(router3_z, 2),
                        'best_ap': best_ap,
                        'ssid': best_ssid,
                        'rssi': round(best_rssi, 2),
                        'distance_to_ap': round(best_distance, 2),
                        'latency_ms': round(latency, 2),
                        'throughput_mbps': round(throughput, 2),
                        'packet_loss_percent': round(packet_loss, 2),
                        'handover_detected': handover_detected,
                        'mesh_connected': mesh_connected
                    })
                    csvfile.flush()
                    
                    # Mostrar resultado do scan
                    status_icon = "🟢" if mesh_connected == "YES" else "🔴"
                    handover_icon = "🔄" if handover_detected == "YES" else "➡️"
                    print_progress(f"{status_icon} Posição: ({rasp_x:.1f},{rasp_y:.1f}) | AP: {best_ap} | RSSI: {best_rssi:.1f} dBm | Dist: {best_distance:.1f}m | Lat: {latency:.1f}ms | {handover_icon}")
                
                time.sleep(2)
        
        print_progress(f"💾 Log salvo em: {log_filename}")
        
        # Ajustar permissões
        try:
            os.chmod(log_filename, 0o666)
            print_progress("🔐 Permissões do arquivo ajustadas")
        except Exception as e:
            print_progress(f"⚠️  Erro ao ajustar permissão do log: {e}")

    # Função de mobilidade do carrinho
    def move_cart():
        print_progress("🚗 Iniciando mobilidade do carrinho...")
        
        # Waypoints para testar conectividade
        waypoints = [
            (0, 0, 0),      # Próximo ao roteador backbone
            (25, 0, 0),     # Meio caminho entre backbone e repetidor
            (50, 50, 0),    # Próximo ao roteador repetidor
            (25, 50, 0),    # Meio caminho de volta
            (0, 25, 0),     # Outro ponto intermediário
            (25, 25, 0),    # Centro da área
        ]
        
        current_waypoint = 0
        waypoint_radius = 5
        total_moves = 30
        
        for i in range(total_moves):
            # Obter waypoint atual
            target_x, target_y, target_z = waypoints[current_waypoint]
            
            # Obter posição atual
            try:
                current_x = float(router3.params.get('x', 25))
                current_y = float(router3.params.get('y', 25))
                current_z = float(router3.params.get('z', 0))
            except:
                current_x, current_y, current_z = 25, 25, 0
            
            # Calcular distância até o waypoint
            distance_to_target = math.sqrt((current_x - target_x)**2 + (current_y - target_y)**2 + (current_z - target_z)**2)
            
            # Se chegou próximo ao waypoint, ir para o próximo
            if distance_to_target < waypoint_radius:
                current_waypoint = (current_waypoint + 1) % len(waypoints)
                target_x, target_y, target_z = waypoints[current_waypoint]
                print_progress(f"🎯 Waypoint alcançado! Indo para próximo ponto: ({target_x}, {target_y})")
            
            # Calcular nova posição (movimento suave)
            step_size = 2.0
            
            # Calcular direção
            dx = target_x - current_x
            dy = target_y - current_y
            dz = target_z - current_z
            
            # Normalizar e aplicar step
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            if distance > 0:
                dx = (dx / distance) * step_size
                dy = (dy / distance) * step_size
                dz = (dz / distance) * step_size
            
            # Nova posição
            new_x = current_x + dx
            new_y = current_y + dy
            new_z = current_z + dz
            
            # Mover roteador móvel e Raspberry Pi
            router3.setPosition(f'{new_x},{new_y},{new_z}')
            raspberry.setPosition(f'{new_x},{new_y},{new_z}')
            
            # Identificar roteador mais próximo
            dist_to_router1 = math.sqrt(new_x**2 + new_y**2)
            dist_to_router2 = math.sqrt((new_x-50)**2 + (new_y-50)**2)
            closest_router = "router1" if dist_to_router1 < dist_to_router2 else "router2"
            closest_distance = min(dist_to_router1, dist_to_router2)
            
            print_progress(f"🚗 Carrinho movido para: ({new_x:.1f}, {new_y:.1f}) | Próximo ao: {closest_router} ({closest_distance:.1f}m)", i+1, total_moves)
            
            time.sleep(2)
        
        print_progress("🏁 Mobilidade do carrinho concluída!")

    print_progress("🔄 Iniciando threads de mobilidade e escaneamento...")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_cart, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Esperar as threads terminarem
    scan_thread.join()
    move_thread.join()
    
    print_progress("🌐 Configurando conectividade de rede...")
    
    print_progress("🔍 Testando conectividade entre dispositivos...")
    net.pingAll()
    
    print_progress("📈 Testando throughput da rede...")
    try:
        # Iniciar servidor iperf no roteador principal
        router1.cmd('iperf -s -t 5 &')
        time.sleep(1)
        
        # Cliente iperf no Raspberry Pi
        result = raspberry.cmd('iperf -c 192.168.1.1 -t 3')
        print_progress(f"📊 Resultado do throughput: {result}")
    except Exception as e:
        print_progress(f"⚠️  Erro no teste de throughput: {e}")
    
    print_progress("✅ Simulação Mastering Scenario 1 concluída com sucesso!")
    
    return net

def main():
    """Função principal"""
    setLogLevel('info')
    
    try:
        net = topology()
        
        # Manter CLI aberto para análise manual
        print_progress("🎮 Abrindo CLI para análise manual...")
        print_progress("💡 Comandos úteis:")
        print_progress("   - nodes: Listar todos os nós")
        print_progress("   - links: Listar todas as conexões")
        print_progress("   - dump: Ver informações detalhadas")
        print_progress("   - pingall: Testar conectividade")
        print_progress("   - iperf: Testar throughput")
        print_progress("   - exit: Sair")
        
        CLI(net)
        
    except KeyboardInterrupt:
        print_progress("🛑 Simulação interrompida pelo usuário")
    except Exception as e:
        print_progress(f"❌ Erro: {e}")
    finally:
        if 'net' in locals():
            net.stop()

if __name__ == '__main__':
    main() 