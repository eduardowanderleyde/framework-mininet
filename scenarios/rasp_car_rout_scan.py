#!/usr/bin/env python3
"""
Cenário: Rasp-Car-Rout (Raspberry + Roteador móvel)
===================================================
- 1 modem principal (AP fixo, recebe internet)
- 1 mesh fixo, 1 mesh móvel (mesh2)
- 1 Raspberry Pi móvel (station) que se move junto com mesh2
- Log em CSV do rasp-car
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

def topology():
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    info("*** Criando nós\n")
    c0 = net.addController('c0', controller=Controller)
    modem = net.addAccessPoint('modem', ssid='Internet', mode='g', channel='1', position='10,30,0', range=58, dpid='1')
    mesh1 = net.addAccessPoint('mesh1', ssid='MeshNet', mode='g', channel='6', position='40,30,0', range=58, dpid='2')
    mesh2 = net.addAccessPoint('mesh2', ssid='MeshNet', mode='g', channel='11', position='70,30,0', range=58, dpid='3')
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='15,25,0')
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    net.build()
    c0.start()
    modem.start([c0])
    mesh1.start([c0])
    mesh2.start([c0])

    def scan_and_log():
        with open('rasp_car_rout_log.csv', 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'position', 'ap', 'rssi', 'distance', 'latency', 'connected']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(10):  # Executar apenas 10 vezes para teste
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
                        distance = rasp.getDistanceTo(ap)
                        # RSSI mais realista baseado em modelo de propagação
                        tx_power = 20  # dBm
                        freq = 2.4e9   # 2.4 GHz
                        c = 3e8        # velocidade da luz
                        fspl = 20 * math.log10(distance) + 20 * math.log10(freq) + 20 * math.log10(4 * math.pi / c)
                        additional_losses = 10  # dB
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
                
                if best_ap:
                    writer.writerow({
                        'timestamp': time.time(), 
                        'position': pos, 
                        'ap': best_ap, 
                        'rssi': round(best_rssi, 2),
                        'distance': round(best_distance, 2),
                        'latency': round(latency, 2),
                        'connected': connected
                    })
                    csvfile.flush()
                    info(f"Log: {pos} -> {best_ap} (RSSI: {best_rssi:.1f} dBm, Dist: {best_distance:.1f}m, Lat: {latency:.1f}ms, Conn: {connected})\n")
                time.sleep(2)

    def move_rasp_and_mesh2():
        positions = [(15,25,0), (35,30,0), (55,30,0), (75,30,0), (35,30,0), (15,25,0)]
        for i in range(10):  # Executar apenas 10 vezes para teste
            pos = positions[i % len(positions)]
            rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            mesh2.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            info(f"Raspberry e Mesh2 movidos para: {pos}\n")
            time.sleep(3)

    info("*** Iniciando threads de mobilidade e escaneamento\n")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_rasp_and_mesh2, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Aguardar um pouco para ver os logs
    time.sleep(15)
    
    info("*** Configurando conectividade\n")
    # Configurar IPs dos APs
    modem.cmd('ifconfig modem-wlan1 10.0.0.1/24')
    mesh1.cmd('ifconfig mesh1-wlan1 10.0.0.2/24')
    mesh2.cmd('ifconfig mesh2-wlan1 10.0.0.3/24')
    
    # Configurar roteamento
    rasp.cmd('route add default gw 10.0.0.1')
    
    info("*** Testando conectividade\n")
    net.pingAll()
    
    # Teste de throughput simples
    info("*** Testando throughput\n")
    try:
        # Iniciar servidor iperf no modem
        modem.cmd('iperf -s -t 5 &')
        time.sleep(1)
        # Teste de throughput do raspberry para o modem
        result = rasp.cmd('iperf -c 10.0.0.1 -t 3')
        info(f"Throughput teste: {result}\n")
    except Exception as e:
        info(f"Erro no teste de throughput: {e}\n")
    
    info("*** Parando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology() 