#!/usr/bin/env python3
"""
Script wrapper para executar cenários do Mininet-WiFi
Facilita a execução com PYTHONPATH configurado automaticamente
"""
import sys
import os
import subprocess
import argparse

def setup_environment():
    """Configura o ambiente para execução do Mininet-WiFi"""
    # Adicionar paths do Mininet-WiFi ao PYTHONPATH
    mininet_path = "/usr/local/lib/python3.12/dist-packages"
    mn_wifi_path = "/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg"
    
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = f"{current_pythonpath}:{mininet_path}:{mn_wifi_path}"
    
    os.environ['PYTHONPATH'] = new_pythonpath
    return new_pythonpath

def run_scenario(scenario_name, verbose=False):
    """Executa um cenário específico"""
    setup_environment()
    
    # Mapear nomes amigáveis para arquivos
    scenarios = {
        'rasp-car': 'scenarios/rasp_car_scan.py',
        'rasp-car-rout': 'scenarios/rasp_car_rout_scan.py',
        'basic': 'scenarios/basic_wifi.py',
        'mesh': 'scenarios/mesh_mobility.py',
        'interference': 'scenarios/interference_test.py',
        'sdn': 'scenarios/sdn_wifi_test.py'
    }
    
    if scenario_name not in scenarios:
        print(f"❌ Cenário '{scenario_name}' não encontrado!")
        print("📋 Cenários disponíveis:")
        for name, path in scenarios.items():
            print(f"   • {name} -> {path}")
        return False
    
    scenario_path = scenarios[scenario_name]
    
    if not os.path.exists(scenario_path):
        print(f"❌ Arquivo do cenário não encontrado: {scenario_path}")
        return False
    
    print(f"🚀 Executando cenário: {scenario_name}")
    print(f"📁 Arquivo: {scenario_path}")
    print(f"🔧 PYTHONPATH configurado: {os.environ['PYTHONPATH']}")
    print("=" * 60)
    
    try:
        # Executar com sudo
        cmd = ['sudo', 'python3', scenario_path]
        result = subprocess.run(cmd, check=True, text=True)
        print("=" * 60)
        print("✅ Cenário executado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar cenário: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário")
        return False

def main():
    parser = argparse.ArgumentParser(description='Executar cenários do Mininet-WiFi')
    parser.add_argument('scenario', help='Nome do cenário para executar')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    print("🎯 Framework Mininet-WiFi - Executor de Cenários")
    print("=" * 60)
    
    success = run_scenario(args.scenario, args.verbose)
    
    if success:
        print("🎉 Execução concluída!")
        sys.exit(0)
    else:
        print("💥 Execução falhou!")
        sys.exit(1)

if __name__ == '__main__':
    main() 