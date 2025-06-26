#!/usr/bin/env python3
"""
🔧 Script Wrapper para Execução de Cenários Mininet-WiFi

Facilita a execução dos cenários com configuração automática do PYTHONPATH
e progresso visual em tempo real.

Autor: Eduardo Wanderley
Data: Dezembro 2024
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime

# Configurar PYTHONPATH automaticamente
def setup_pythonpath():
    """Configura o PYTHONPATH para incluir Mininet-WiFi"""
    mininet_paths = [
        "/usr/local/lib/python3.12/dist-packages",
        "/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg",
        "/usr/local/lib/python3.12/dist-packages/mininet_wifi-2.6-py3.12.egg/mn_wifi"
    ]
    
    current_path = os.environ.get('PYTHONPATH', '')
    for path in mininet_paths:
        if path not in current_path:
            if current_path:
                current_path += ':' + path
            else:
                current_path = path
    
    os.environ['PYTHONPATH'] = current_path
    return current_path

def get_scenarios():
    """Retorna dicionário com todos os cenários disponíveis"""
    return {
        'basic': {
            'file': 'scenarios/basic_wifi.py',
            'description': 'Cenário básico Wi-Fi com AP e estações'
        },
        'mesh': {
            'file': 'scenarios/mesh_mobility.py', 
            'description': 'Rede mesh com mobilidade'
        },
        'interference': {
            'file': 'scenarios/interference_test.py',
            'description': 'Teste de interferência entre APs'
        },
        'sdn': {
            'file': 'scenarios/sdn_wifi_test.py',
            'description': 'Validação SDN com Wi-Fi'
        },
        'rasp-car': {
            'file': 'scenarios/rasp_car_scan.py',
            'description': 'Raspberry Pi móvel escaneando rede mesh'
        },
        'rasp-car-rout': {
            'file': 'scenarios/rasp_car_rout_scan.py',
            'description': 'Raspberry Pi + roteador móvel em carrinho'
        },
        'mastering-1': {
            'file': 'scenarios/mastering-scenario-1.py',
            'description': '🎯 Mastering Scenario 1: 3 roteadores mesh + Raspberry Pi móvel em carrinho'
        }
    }

def print_banner():
    """Exibe banner do framework"""
    print("🎯 Framework Mininet-WiFi - Executor de Cenários")
    print("=" * 60)

def print_scenarios():
    """Lista todos os cenários disponíveis"""
    print("\n📋 Cenários Disponíveis:")
    print("-" * 60)
    for key, scenario in get_scenarios().items():
        print(f"  {key:20} - {scenario['description']}")
    print("-" * 60)

def run_scenario(scenario_name, verbose=False):
    """Executa um cenário específico"""
    if scenario_name not in get_scenarios():
        print(f"❌ Cenário '{scenario_name}' não encontrado!")
        print_scenarios()
        return False
    
    scenario = get_scenarios()[scenario_name]
    script_file = scenario['file']
    
    # Verificar se arquivo existe
    if not os.path.exists(script_file):
        print(f"❌ Arquivo do cenário não encontrado: {script_file}")
        return False
    
    print_banner()
    print(f"🚀 Executando cenário: {scenario_name}")
    print(f"📁 Arquivo: {script_file}")
    print(f"🔧 PYTHONPATH configurado: {setup_pythonpath()}")
    print("=" * 60)
    
    try:
        # Executar com sudo
        cmd = ['sudo', 'python3', script_file]
        
        if verbose:
            print(f"🔍 Comando: {' '.join(cmd)}")
        
        print(f"ℹ️  🚀 Iniciando simulação {scenario_name}...")
        
        # Executar o cenário
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Cenário executado com sucesso!")
            print("🎉 Execução concluída!")
            return True
        else:
            print(f"❌ Erro na execução do cenário (código: {result.returncode})")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Executor de cenários Mininet-WiFi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python3 run_scenario.py rasp-car
  python3 run_scenario.py mastering-scenario-1
  python3 run_scenario.py --list
  python3 run_scenario.py --help
        """
    )
    
    parser.add_argument(
        'scenario',
        nargs='?',
        help='Nome do cenário a executar'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Listar todos os cenários disponíveis'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verboso com mais informações'
    )
    
    args = parser.parse_args()
    
    # Listar cenários se solicitado
    if args.list:
        print_banner()
        print_scenarios()
        return
    
    # Verificar se cenário foi especificado
    if not args.scenario:
        print_banner()
        print("❌ Nenhum cenário especificado!")
        print_scenarios()
        print("\n💡 Use: python3 run_scenario.py <cenário>")
        print("💡 Use: python3 run_scenario.py --list para ver opções")
        return
    
    # Executar cenário
    success = run_scenario(args.scenario, args.verbose)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 