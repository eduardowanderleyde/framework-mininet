#!/usr/bin/env python3
"""
Script de teste para verificar posições do Raspberry Pi
"""
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.link import wmediumd
from mn_wifi.net import Mininet_wifi
import time

def topology():
    info("🚀 Iniciando teste de posições...\n")
    
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    c0 = net.addController('c0', controller=Controller)
    
    # Modem principal
    modem = net.addAccessPoint('modem', ssid='Internet', mode='g', channel='1', position='10,30,0', range=58, dpid='1')
    
    # Raspberry Pi móvel
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='15,25,0')
    
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    net.build()
    c0.start()
    modem.start([c0])
    
    info("✅ Rede criada!\n")
    
    # Testar diferentes posições
    positions = [(15,25,0), (35,30,0), (55,30,0), (75,30,0)]
    
    for i, pos in enumerate(positions):
        info(f"📍 Movendo para posição {i+1}: {pos}\n")
        rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
        time.sleep(1)
        
        # Tentar diferentes métodos para obter posição
        try:
            # Método 1: params
            pos1 = f"{rasp.params.get('x', 'N/A')},{rasp.params.get('y', 'N/A')},{rasp.params.get('z', 'N/A')}"
            info(f"   Método 1 (params): {pos1}\n")
        except Exception as e:
            info(f"   Método 1 erro: {e}\n")
        
        try:
            # Método 2: position
            pos2 = rasp.position
            info(f"   Método 2 (position): {pos2}\n")
        except Exception as e:
            info(f"   Método 2 erro: {e}\n")
        
        try:
            # Método 3: coords
            pos3 = rasp.coords
            info(f"   Método 3 (coords): {pos3}\n")
        except Exception as e:
            info(f"   Método 3 erro: {e}\n")
        
        info("   ---\n")
    
    info("🛑 Finalizando teste...\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology() 