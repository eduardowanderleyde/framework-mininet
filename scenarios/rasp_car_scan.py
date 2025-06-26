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
import math
import os


def print_progress(message, step=None, total=None):
    """Função para imprimir progresso de forma clara"""
    if step and total:
        progress = (step / total) * 100
        info(f"🔄 [{progress:.0f}%] {message}\n")
    else:
        info(f"ℹ️  {message}\n")


def topology():
    print_progress("🚀 Iniciando simulação Rasp-Car Scanner...")
    
    net = Mininet_wifi(controller=Controller, link=wmediumd, accessPoint=OVSKernelAP)
    
    print_progress("📡 Criando rede Wi-Fi mesh...")
    c0 = net.addController('c0', controller=Controller)
    
    # Modem principal (AP fixo)
    print_progress("🔌 Configurando modem principal...")
    modem = net.addAccessPoint('modem', ssid='Internet', mode='g', channel='1', position='10,30,0', range=58, dpid='1')
    
    # Mesh routers
    print_progress("🌐 Configurando roteadores mesh...")
    mesh1 = net.addAccessPoint('mesh1', ssid='MeshNet', mode='g', channel='6', position='40,30,0', range=58, dpid='2')
    mesh2 = net.addAccessPoint('mesh2', ssid='MeshNet', mode='g', channel='11', position='70,30,0', range=58, dpid='3')
    
    # Raspberry Pi móvel
    print_progress("📱 Configurando Raspberry Pi móvel...")
    rasp = net.addStation('rasp', ip='10.0.0.10/24', position='15,25,0')
    
    print_progress("⚙️  Configurando modelo de propagação...")
    net.setPropagationModel(model="logDistance", exp=3.5)
    net.configureWifiNodes()
    
    print_progress("🔨 Construindo rede...")
    net.build()
    
    print_progress("🎮 Iniciando controlador...")
    c0.start()
    
    print_progress("📶 Ativando access points...")
    modem.start([c0])
    mesh1.start([c0])
    mesh2.start([c0])
    
    print_progress("✅ Rede Wi-Fi mesh ativada com sucesso!")

    # Função de escaneamento e log em CSV
    def scan_and_log():
        print_progress("📊 Iniciando sistema de escaneamento e log...")
        log_filename = 'rasp_car_scan_log.csv'
        
        with open(log_filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'position', 'ap', 'rssi', 'distance', 'latency', 'connected']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total_scans = 10
            for i in range(total_scans):
                print_progress(f"🔍 Escaneando rede (ciclo {i+1}/{total_scans})...", i+1, total_scans)
                
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
                        # RSSI = Potência_transmissão - Perdas_espaço_livre - Perdas_adicionais
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
                        info(f"⚠️  Erro ao calcular RSSI para {ap.name}: {e}\n")
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
                    
                    # Mostrar resultado do scan de forma clara
                    status_icon = "🟢" if connected == "YES" else "🔴"
                    print_progress(f"{status_icon} Posição: {pos} | AP: {best_ap} | RSSI: {best_rssi:.1f} dBm | Dist: {best_distance:.1f}m | Lat: {latency:.1f}ms")
                
                time.sleep(2)
        
        print_progress(f"💾 Log salvo em: {log_filename}")
        
        # Corrigir permissão do arquivo para o usuário normal
        try:
            os.system(f'chown $SUDO_USER:$SUDO_USER {log_filename}')
            print_progress("🔐 Permissões do arquivo ajustadas")
        except Exception as e:
            print_progress(f"⚠️  Erro ao ajustar permissão do log: {e}")

    # Função de mobilidade do rasp-car
    def move_rasp():
        print_progress("🚗 Iniciando mobilidade do Raspberry Pi...")
        positions = [(15,25,0), (35,30,0), (55,30,0), (75,30,0), (35,30,0), (15,25,0)]
        total_moves = 10
        
        for i in range(total_moves):
            pos = positions[i % len(positions)]
            rasp.setPosition(f'{pos[0]},{pos[1]},{pos[2]}')
            print_progress(f"📍 Raspberry movido para: ({pos[0]}, {pos[1]}, {pos[2]})", i+1, total_moves)
            time.sleep(3)
        
        print_progress("🏁 Mobilidade concluída!")

    print_progress("🔄 Iniciando threads de mobilidade e escaneamento...")
    scan_thread = threading.Thread(target=scan_and_log, daemon=True)
    move_thread = threading.Thread(target=move_rasp, daemon=True)
    
    scan_thread.start()
    move_thread.start()
    
    # Esperar as threads terminarem
    scan_thread.join()
    move_thread.join()
    
    print_progress("🌐 Configurando conectividade de rede...")
    # Configurar IPs dos APs
    modem.cmd('ifconfig modem-wlan1 10.0.0.1/24')
    mesh1.cmd('ifconfig mesh1-wlan1 10.0.0.2/24')
    mesh2.cmd('ifconfig mesh2-wlan1 10.0.0.3/24')
    
    # Configurar roteamento
    rasp.cmd('route add default gw 10.0.0.1')
    
    print_progress("🔍 Testando conectividade entre dispositivos...")
    net.pingAll()
    
    # Teste de throughput simples
    print_progress("📈 Testando throughput da rede...")
    try:
        # Iniciar servidor iperf no modem
        modem.cmd('iperf -s -t 5 &')
        time.sleep(1)
        # Teste de throughput do raspberry para o modem
        result = rasp.cmd('iperf -c 10.0.0.1 -t 3')
        print_progress(f"📊 Resultado do throughput: {result}")
    except Exception as e:
        print_progress(f"⚠️  Erro no teste de throughput: {e}")
    
    print_progress("🛑 Finalizando simulação...")
    net.stop()
    print_progress("✅ Simulação Rasp-Car Scanner concluída com sucesso!")

if __name__ == '__main__':
    setLogLevel('info')
    topology() 