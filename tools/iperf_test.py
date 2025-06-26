#!/usr/bin/env python3
"""
Ferramenta de Teste de Throughput com iperf
===========================================

Esta ferramenta executa testes de throughput em redes Wi-Fi usando iperf:
- Teste de throughput entre dispositivos
- Análise de performance sob diferentes condições
- Geração de relatórios de performance

Autor: Framework Mininet-WiFi
Data: 2024
"""

import subprocess
import time
import json
import argparse
from datetime import datetime


class IperfTester:
    """Classe para executar testes de throughput com iperf"""
    
    def __init__(self, duration=10, interval=1):
        self.duration = duration
        self.interval = interval
        self.results = []
    
    def run_iperf_test(self, server_ip, client_ip, port=5201):
        """Executa teste de throughput entre dois dispositivos"""
        print(f"🚀 Iniciando teste de throughput: {client_ip} -> {server_ip}")
        
        # Iniciar servidor iperf
        server_cmd = f"iperf -s -p {port} -t {self.duration}"
        server_process = subprocess.Popen(server_cmd.split(), 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        time.sleep(2)  # Aguardar servidor iniciar
        
        # Executar cliente iperf
        client_cmd = f"iperf -c {server_ip} -p {port} -t {self.duration} -i {self.interval}"
        client_process = subprocess.Popen(client_cmd.split(), 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Capturar saída
        stdout, stderr = client_process.communicate()
        
        # Parar servidor
        server_process.terminate()
        
        # Analisar resultados
        result = self.parse_iperf_output(stdout.decode())
        result['server_ip'] = server_ip
        result['client_ip'] = client_ip
        result['timestamp'] = datetime.now().isoformat()
        
        self.results.append(result)
        return result
    
    def parse_iperf_output(self, output):
        """Analisa saída do iperf e extrai métricas"""
        lines = output.split('\n')
        result = {
            'bandwidth': 0,
            'transfer': 0,
            'retransmits': 0,
            'errors': 0
        }
        
        for line in lines:
            if 'bits/sec' in line:
                # Extrair bandwidth
                parts = line.split()
                if len(parts) >= 7:
                    bandwidth = float(parts[6])
                    unit = parts[7]
                    # Converter para Mbps
                    if 'Kbits' in unit:
                        bandwidth /= 1000
                    elif 'Gbits' in unit:
                        bandwidth *= 1000
                    result['bandwidth'] = bandwidth
            
            elif 'transfer' in line:
                # Extrair transfer
                parts = line.split()
                if len(parts) >= 5:
                    transfer = float(parts[4])
                    unit = parts[5]
                    # Converter para MB
                    if 'KBytes' in unit:
                        transfer /= 1024
                    elif 'GBytes' in unit:
                        transfer *= 1024
                    result['transfer'] = transfer
        
        return result
    
    def run_multiple_tests(self, test_configs):
        """Executa múltiplos testes de throughput"""
        print(f"🔄 Executando {len(test_configs)} testes de throughput...")
        
        for i, config in enumerate(test_configs, 1):
            print(f"\n📊 Teste {i}/{len(test_configs)}")
            result = self.run_iperf_test(
                config['server_ip'],
                config['client_ip'],
                config.get('port', 5201)
            )
            print(f"   Throughput: {result['bandwidth']:.2f} Mbps")
            print(f"   Transfer: {result['transfer']:.2f} MB")
            time.sleep(2)
    
    def generate_report(self, filename=None):
        """Gera relatório dos testes"""
        if not filename:
            filename = f"iperf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'results': self.results,
            'summary': self.calculate_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Relatório salvo em: {filename}")
        return report
    
    def calculate_summary(self):
        """Calcula estatísticas dos resultados"""
        if not self.results:
            return {}
        
        bandwidths = [r['bandwidth'] for r in self.results]
        transfers = [r['transfer'] for r in self.results]
        
        return {
            'avg_bandwidth': sum(bandwidths) / len(bandwidths),
            'max_bandwidth': max(bandwidths),
            'min_bandwidth': min(bandwidths),
            'avg_transfer': sum(transfers) / len(transfers),
            'total_transfer': sum(transfers)
        }


def main():
    parser = argparse.ArgumentParser(description='Teste de throughput com iperf')
    parser.add_argument('--server', required=True, help='IP do servidor')
    parser.add_argument('--client', required=True, help='IP do cliente')
    parser.add_argument('--duration', type=int, default=10, help='Duração do teste (s)')
    parser.add_argument('--interval', type=int, default=1, help='Intervalo de relatório (s)')
    parser.add_argument('--port', type=int, default=5201, help='Porta do iperf')
    parser.add_argument('--report', help='Arquivo de relatório')
    
    args = parser.parse_args()
    
    # Criar tester
    tester = IperfTester(duration=args.duration, interval=args.interval)
    
    # Executar teste
    result = tester.run_iperf_test(args.server, args.client, args.port)
    
    # Mostrar resultados
    print(f"\n📊 Resultados do teste:")
    print(f"   Servidor: {result['server_ip']}")
    print(f"   Cliente: {result['client_ip']}")
    print(f"   Throughput: {result['bandwidth']:.2f} Mbps")
    print(f"   Transfer: {result['transfer']:.2f} MB")
    print(f"   Timestamp: {result['timestamp']}")
    
    # Gerar relatório
    if args.report:
        tester.generate_report(args.report)
    else:
        tester.generate_report()


if __name__ == '__main__':
    main() 