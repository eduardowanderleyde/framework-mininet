#!/usr/bin/env python3
"""
Cenário: Rasp-Car Scanner (Versão Estendida)
============================================
- 1 modem principal (AP fixo, recebe internet)
- 2 roteadores mesh (APs mesh, interconectados)
- 1 Raspberry Pi móvel (station) que escaneia e loga sinais Wi-Fi em CSV
- Versão com mais dados e posições variadas
"""
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import time
import threading
import csv
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
    # Raspberry Pi móvel - posição inicial diferente
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='25,25,0')
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    net.build()
    c0.start()
    modem.start([c0])
    mesh1.start([c0])
    mesh2.start([c0])

    # Função de escaneamento e log em CSV
    def scan_and_log():
        log_filename = 'rasp_car_scan_extended_log.csv'
        with open(log_filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'position', 'ap', 'rssi', 'distance', 'latency', 'connected', 'signal_quality']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(20):  # Mais iterações
                # Obter posição de forma mais segura
                try:
                    pos = f"{rasp.params.get('x', 0)},{rasp.params.get('y', 0)},{rasp.params.get('z', 0)}"
                except:
                    pos = "0,0,0"
                
                best_ap = None
                best_rssi = -999
                best_distance = 999
                
                for ap in [modem, mesh1, mesh2]:
                    try:
                        # Calcular distância manualmente usando coordenadas
                        rasp_x = float(rasp.params.get('x', 0))
                        rasp_y = float(rasp.params.get('y', 0))
                        rasp_z = float(rasp.params.get('z', 0))
                        
                        ap_x = float(ap.params.get('x', 0))
                        ap_y = float(ap.params.get('y', 0))
                        ap_z = float(ap.params.get('z', 0))
                        
                        distance = math.sqrt((rasp_x - ap_x)**2 + (rasp_y - ap_y)**2 + (rasp_z - ap_z)**2)
                        if distance < 0.01:
                            distance = 0.01  # evitar log(0)
                        
                        # RSSI mais realista baseado em modelo de propagação
                        tx_power = 20  # dBm (potência de transmissão típica)
                        freq = 2.4e9   # 2.4 GHz
                        c = 3e8        # velocidade da luz
                        fspl = 20 * math.log10(distance) + 20 * math.log10(freq) + 20 * math.log10(4 * math.pi / c)
                        additional_losses = 10  # dB (paredes, obstáculos, etc.)
                        rssi = tx_power - fspl - additional_losses
                        
                        if rssi > best_rssi:
                            best_rssi = rssi
                            best_ap = ap.name
                            best_distance = distance
                    except Exception as e:
                        info(f"Erro ao calcular RSSI para {ap.name}: {e}\n")
                        continue
                
                # Calcular latência simulada baseada na distância
                latency = 5 + (best_distance * 0.1) if best_distance < 999 else 999
                
                # Verificar conectividade (RSSI > -70 dBm)
                connected = "YES" if best_rssi > -70 else "NO"
                
                # Qualidade do sinal baseada no RSSI
                if best_rssi > -50:
                    signal_quality = "EXCELLENT"
                elif best_rssi > -60:
                    signal_quality = "GOOD"
                elif best_rssi > -70:
                    signal_quality = "FAIR"
                else:
                    signal_quality = "POOR"
                
                if best_ap:
                    writer.writerow({
                        'timestamp': time.time(), 
                        'position': pos, 
                        'ap': best_ap, 
                        'rssi': round(best_rssi, 2),
                        'distance': round(best_distance, 2),
                        'latency': round(latency, 2),
                        'connected': connected,
                        'signal_quality': signal_quality
                    })
                    csvfile.flush()
                    info(f"Log: {pos} -> {best_ap} (RSSI: {best_rssi:.1f} dBm, Dist: {best_distance:.1f}m, Lat: {latency:.1f}ms, Conn: {connected}, Quality: {signal_quality})\n")
                time.sleep(1)  # Mais rápido
        # Corrigir permissão do arquivo para o usuário normal
        try:
            os.system(f'chown $SUDO_USER:$SUDO_USER {log_filename}')
        except Exception as e:
            info(f"Erro ao ajustar permissão do log: {e}\n")

    # Função de mobilidade do rasp-car com mais posições
    def move_rasp():
        positions = [
            (25,25,0), (35,30,0), (45,30,0), (55,30,0), (65,30,0), (75,30,0),
            (65,30,0), (55,30,0), (45,30,0), (35,30,0), (25,25,0), (15,25,0),
            (25,25,0), (35,30,0), (45,30,0), (55,30,0), (65,30,0), (75,30,0),
            (65,30,0), (55,30,0)
        ]
        for i in range(20):  # Mais iterações
            pos = positions[i % len(positions)]
            rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            info(f"Raspberry movido para: {pos}\n")
            time.sleep(1.5)  # Mais rápido

    info("*** Iniciando threads de mobilidade e escaneamento\n")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_rasp, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Esperar as threads terminarem
    scan_thread.join()
    move_thread.join()
    
    info("*** Configurando conectividade\n")
    # Configurar IPs dos APs
    modem.cmd('ifconfig modem-wlan1 10.0.0.1/24')
    mesh1.cmd('ifconfig mesh1-wlan1 10.0.0.2/24')
    mesh2.cmd('ifconfig mesh2-wlan1 10.0.0.3/24')
    
    # Configurar roteamento
    rasp.cmd('route add default gw 10.0.0.1')
    
    info("*** Testando conectividade\n")
    net.pingAll()
    
    info("*** Parando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology() 