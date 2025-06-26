#!/usr/bin/env python3
"""
Script wrapper para executar cenários Mininet-WiFi
Ajusta o PYTHONPATH automaticamente e executa com sudo
"""
import sys
import os
import subprocess

def run_scenario(scenario_name):
    """Executa um cenário específico"""
    # Executar o cenário com sudo
    scenario_file = f'scenarios/{scenario_name}.py'
    if not os.path.exists(scenario_file):
        print(f"❌ Cenário {scenario_file} não encontrado!")
        return False
    
    print(f"🚀 Executando cenário: {scenario_name}")
    print(f"📁 Arquivo: {scenario_file}")
    print("⏳ Aguarde... (pode demorar alguns segundos)")
    print("🔐 Executando com sudo (Mininet-WiFi requer privilégios de root)")
    
    try:
        # Executar com sudo e PYTHONPATH ajustado
        cmd = [
            'sudo', 'PYTHONPATH=/usr/local/lib/python3.12/dist-packages', 
            'python3', scenario_file
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ Cenário executado com sucesso!")
            print("📊 Logs gerados:")
            
            # Verificar logs gerados
            log_files = [f'{scenario_name}_log.csv', f'{scenario_name}_rout_log.csv']
            for log_file in log_files:
                if os.path.exists(log_file):
                    size = os.path.getsize(log_file)
                    if size > 0:
                        print(f"   📄 {log_file} ({size} bytes)")
                        # Mostrar primeiras linhas
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            print(f"   📋 {len(lines)} linhas")
                            if len(lines) > 1:
                                print(f"   📊 Dados: {len(lines)-1} registros")
                                # Mostrar alguns dados de exemplo
                                print("   📈 Exemplo de dados:")
                                for i, line in enumerate(lines[1:4]):  # Primeiras 3 linhas de dados
                                    print(f"      {line.strip()}")
                    else:
                        print(f"   ⚠️  {log_file} (vazio)")
                else:
                    print(f"   ❌ {log_file} (não encontrado)")
        else:
            print("❌ Erro ao executar cenário:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - cenário demorou muito para executar")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 run_scenario.py <cenario>")
        print("Cenários disponíveis:")
        print("  - rasp_car_scan")
        print("  - rasp_car_rout_scan")
        sys.exit(1)
    
    scenario = sys.argv[1]
    run_scenario(scenario) 