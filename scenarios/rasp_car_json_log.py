#!/usr/bin/env python3
"""
Cenário: Rasp-Car Scanner (Log JSON)
====================================
- 1 modem principal (AP fixo, recebe internet)
- 2 roteadores mesh (APs mesh, interconectados)
- 1 Raspberry Pi móvel (station) que escaneia e loga sinais Wi-Fi em JSON
- Demonstração de formato de log alternativo
"""
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import time
import threading
import json
import math
import os


def topology():
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    info("*** Criando nós\n")
    c0 = net.addController('c0', controller=Controller)
    # Modem principal (AP fixo)
    modem = net.addAccessPoint('modem', ssid='Internet', mode='g', channel='1', position='10,30,0', range=58, dpid='1')
    # Mesh routers
    mesh1 = net.addAccessPoint('mesh1', ssid='MeshNet', mode='g', channel='6', position='40,30,0', range=58, dpid='2')
    mesh2 = net.addAccessPoint('mesh2', ssid='MeshNet', mode='g', channel='11', position='70,30,0', range=58, dpid='3')
    # Raspberry Pi móvel
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='20,20,0')
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    net.build()
    c0.start()
    modem.start([c0])
    mesh1.start([c0])
    mesh2.start([c0])

    # Função de escaneamento e log em JSON
    def scan_and_log():
        log_filename = 'rasp_car_json_log.json'
        logs = []
        for i in range(15):  # 15 iterações
            # Obter posição
            try:
                pos = {
                    'x': float(rasp.params.get('x', 0)),
                    'y': float(rasp.params.get('y', 0)),
                    'z': float(rasp.params.get('z', 0))
                }
            except:
                pos = {'x': 0, 'y': 0, 'z': 0}
            
            ap_data = []
            
            for ap in [modem, mesh1, mesh2]:
                try:
                    # Calcular distância
                    rasp_x = float(rasp.params.get('x', 0))
                    rasp_y = float(rasp.params.get('y', 0))
                    rasp_z = float(rasp.params.get('z', 0))
                    
                    ap_x = float(ap.params.get('x', 0))
                    ap_y = float(ap.params.get('y', 0))
                    ap_z = float(ap.params.get('z', 0))
                    
                    distance = math.sqrt((rasp_x - ap_x)**2 + (rasp_y - ap_y)**2 + (rasp_z - ap_z)**2)
                    if distance < 0.01:
                        distance = 0.01
                    
                    # RSSI realista
                    tx_power = 20
                    freq = 2.4e9
                    c = 3e8
                    fspl = 20 * math.log10(distance) + 20 * math.log10(freq) + 20 * math.log10(4 * math.pi / c)
                    additional_losses = 10
                    rssi = tx_power - fspl - additional_losses
                    
                    # Latência
                    latency = 5 + (distance * 0.1)
                    
                    # Conectividade
                    connected = rssi > -70
                    
                    ap_data.append({
                        'name': ap.name,
                        'ssid': ap.params.get('ssid', 'Unknown'),
                        'channel': ap.params.get('channel', 'Unknown'),
                        'rssi': round(rssi, 2),
                        'distance': round(distance, 2),
                        'latency': round(latency, 2),
                        'connected': connected,
                        'signal_strength': 'strong' if rssi > -50 else 'medium' if rssi > -60 else 'weak'
                    })
                    
                except Exception as e:
                    info(f"Erro ao calcular dados para {ap.name}: {e}\n")
                    continue
            
            # Encontrar melhor AP
            best_ap = max(ap_data, key=lambda x: x['rssi']) if ap_data else None
            
            log_entry = {
                'timestamp': time.time(),
                'timestamp_readable': time.strftime('%Y-%m-%d %H:%M:%S'),
                'iteration': i + 1,
                'position': pos,
                'available_aps': ap_data,
                'best_ap': best_ap,
                'network_status': {
                    'total_aps': len(ap_data),
                    'connected_aps': len([ap for ap in ap_data if ap['connected']]),
                    'best_signal': best_ap['rssi'] if best_ap else -999
                }
            }
            
            logs.append(log_entry)
            info(f"Log JSON: Iteração {i+1}, Melhor AP: {best_ap['name'] if best_ap else 'None'} (RSSI: {best_ap['rssi'] if best_ap else 'N/A'})\n")
            time.sleep(1.5)
        
        # Salvar logs em JSON
        with open(log_filename, 'w') as jsonfile:
            json.dump({
                'scenario': 'rasp_car_json_log',
                'description': 'Raspberry Pi mobile scanning with JSON logging',
                'total_iterations': len(logs),
                'logs': logs
            }, jsonfile, indent=2)
        
        # Corrigir permissão
        try:
            os.system(f'chown $SUDO_USER:$SUDO_USER {log_filename}')
        except Exception as e:
            info(f"Erro ao ajustar permissão do log: {e}\n")

    # Função de mobilidade
    def move_rasp():
        positions = [
            (20,20,0), (30,25,0), (40,25,0), (50,25,0), (60,25,0),
            (50,25,0), (40,25,0), (30,25,0), (20,20,0), (10,20,0),
            (20,20,0), (30,25,0), (40,25,0), (50,25,0), (60,25,0)
        ]
        for i in range(15):
            pos = positions[i % len(positions)]
            rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            info(f"Raspberry movido para: {pos}\n")
            time.sleep(2)

    info("*** Iniciando threads de mobilidade e escaneamento\n")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_rasp, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Esperar as threads terminarem
    scan_thread.join()
    move_thread.join()
    
    info("*** Configurando conectividade\n")
    modem.cmd('ifconfig modem-wlan1 10.0.0.1/24')
    mesh1.cmd('ifconfig mesh1-wlan1 10.0.0.2/24')
    mesh2.cmd('ifconfig mesh2-wlan1 10.0.0.3/24')
    rasp.cmd('route add default gw 10.0.0.1')
    
    info("*** Testando conectividade\n")
    net.pingAll()
    
    info("*** Parando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology() 