#!/usr/bin/env python3
"""
Cenário: Rasp-Car Scanner
========================
- 1 modem principal (AP fixo, recebe internet)
- 2 roteadores mesh (APs mesh, interconectados)
- 1 Raspberry Pi móvel (station) que escaneia e loga sinais Wi-Fi em CSV
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


def topology():
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    info("*** Criando nós\n")
    c0 = net.addController('c0', controller=Controller)
    # Modem principal (AP fixo)
    modem = net.addAccessPoint('modem', ssid='Internet', mode='g', channel='1', position='10,30,0', range=25, dpid='1')
    # Mesh routers
    mesh1 = net.addAccessPoint('mesh1', ssid='MeshNet', mode='g', channel='6', position='40,30,0', range=25, dpid='2')
    mesh2 = net.addAccessPoint('mesh2', ssid='MeshNet', mode='g', channel='11', position='70,30,0', range=25, dpid='3')
    # Raspberry Pi móvel
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='15,25,0')
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    net.build()
    c0.start()
    modem.start([c0])
    mesh1.start([c0])
    mesh2.start([c0])

    # Função de escaneamento e log em CSV
    def scan_and_log():
        with open('rasp_car_log.csv', 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'position', 'ap', 'rssi']
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
                for ap in [modem, mesh1, mesh2]:
                    try:
                        rssi = -50 - (rasp.getDistanceTo(ap) * 2)
                        if rssi > best_rssi:
                            best_rssi = rssi
                            best_ap = ap.name
                    except:
                        continue
                
                if best_ap:
                    writer.writerow({'timestamp': time.time(), 'position': pos, 'ap': best_ap, 'rssi': best_rssi})
                    csvfile.flush()
                    info(f"Log: {pos} -> {best_ap} (RSSI: {best_rssi:.1f})\n")
                time.sleep(2)

    # Função de mobilidade do rasp-car
    def move_rasp():
        positions = [(15,25,0), (35,30,0), (55,30,0), (75,30,0), (35,30,0), (15,25,0)]
        for i in range(10):  # Executar apenas 10 vezes para teste
            pos = positions[i % len(positions)]
            rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            info(f"Raspberry movido para: {pos}\n")
            time.sleep(3)

    info("*** Iniciando threads de mobilidade e escaneamento\n")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_rasp, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Aguardar um pouco para ver os logs
    time.sleep(15)
    
    info("*** Testando conectividade\n")
    net.pingAll()
    
    info("*** Parando rede\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology() 