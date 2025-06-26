#!/usr/bin/env python3
"""
Interface Web Simples para Framework Mininet-WiFi
=================================================
Servidor web local para configurar e executar cenários de forma visual
"""
from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import json
import time
import threading
from datetime import datetime

app = Flask(__name__)

# Configurações globais
SCENARIOS = {
    'rasp_car_scan': {
        'name': 'Rasp-Car Scanner',
        'description': 'Raspberry Pi móvel escaneando sinais Wi-Fi',
        'file': 'scenarios/rasp_car_scan.py',
        'log_file': 'rasp_car_scan_log.csv'
    },
    'rasp_car_rout_scan': {
        'name': 'Rasp-Car-Rout',
        'description': 'Raspberry Pi + Roteador móvel',
        'file': 'scenarios/rasp_car_rout_scan.py',
        'log_file': 'rasp_car_rout_scan_log.csv'
    },
    'rasp_car_scan_extended': {
        'name': 'Rasp-Car Extended',
        'description': 'Versão estendida com mais dados',
        'file': 'scenarios/rasp_car_scan_extended.py',
        'log_file': 'rasp_car_scan_extended_log.csv'
    },
    'rasp_car_json_log': {
        'name': 'Rasp-Car JSON',
        'description': 'Log em formato JSON estruturado',
        'file': 'scenarios/rasp_car_json_log.py',
        'log_file': 'rasp_car_json_log.json'
    }
}

# Status da execução
execution_status = {
    'running': False,
    'current_scenario': None,
    'progress': 0,
    'log': []
}

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', scenarios=SCENARIOS)

@app.route('/api/run_scenario', methods=['POST'])
def run_scenario():
    """Executa um cenário"""
    data = request.get_json()
    scenario_id = data.get('scenario')
    
    if scenario_id not in SCENARIOS:
        return jsonify({'error': 'Cenário não encontrado'}), 400
    
    if execution_status['running']:
        return jsonify({'error': 'Já há uma execução em andamento'}), 400
    
    # Iniciar execução em thread separada
    thread = threading.Thread(target=execute_scenario, args=(scenario_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Execução iniciada', 'scenario': scenario_id})

@app.route('/api/status')
def get_status():
    """Retorna o status atual da execução"""
    return jsonify(execution_status)

@app.route('/api/logs')
def get_logs():
    """Lista todos os logs disponíveis"""
    logs = []
    for scenario_id, config in SCENARIOS.items():
        log_file = config['log_file']
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            modified = datetime.fromtimestamp(os.path.getmtime(log_file))
            logs.append({
                'scenario': scenario_id,
                'name': config['name'],
                'file': log_file,
                'size': size,
                'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                'format': 'JSON' if log_file.endswith('.json') else 'CSV'
            })
    
    return jsonify(logs)

@app.route('/api/view_log/<filename>')
def view_log(filename):
    """Visualiza um arquivo de log"""
    if not os.path.exists(filename):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        if filename.endswith('.json'):
            with open(filename, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            # CSV - retornar primeiras linhas
            with open(filename, 'r') as f:
                lines = f.readlines()
            return jsonify({
                'type': 'csv',
                'lines': lines[:20],  # Primeiras 20 linhas
                'total_lines': len(lines)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_log(filename):
    """Download de um arquivo de log"""
    if not os.path.exists(filename):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    return send_file(filename, as_attachment=True)

def execute_scenario(scenario_id):
    """Executa um cenário em background"""
    global execution_status
    
    execution_status['running'] = True
    execution_status['current_scenario'] = scenario_id
    execution_status['progress'] = 0
    execution_status['log'] = []
    
    scenario_config = SCENARIOS[scenario_id]
    
    try:
        # Adicionar log de início
        execution_status['log'].append(f"Iniciando cenário: {scenario_config['name']}")
        execution_status['progress'] = 10
        
        # Comando para executar
        cmd = [
            'sudo', 
            'PYTHONPATH=/usr/local/lib/python3.12/dist-packages',
            'python3', 
            scenario_config['file']
        ]
        
        execution_status['log'].append("Executando com Mininet-WiFi...")
        execution_status['progress'] = 30
        
        # Executar o cenário
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutos de timeout
        )
        
        execution_status['progress'] = 80
        
        if result.returncode == 0:
            execution_status['log'].append("✅ Cenário executado com sucesso!")
            execution_status['log'].append(f"📄 Log gerado: {scenario_config['log_file']}")
            
            # Verificar se o log foi criado
            if os.path.exists(scenario_config['log_file']):
                size = os.path.getsize(scenario_config['log_file'])
                execution_status['log'].append(f"📊 Tamanho do log: {size} bytes")
                
                # Corrigir permissões
                os.system(f'chown $SUDO_USER:$SUDO_USER {scenario_config["log_file"]}')
                execution_status['log'].append("🔧 Permissões corrigidas")
        else:
            execution_status['log'].append(f"❌ Erro na execução: {result.stderr}")
        
        execution_status['progress'] = 100
        
    except subprocess.TimeoutExpired:
        execution_status['log'].append("⏰ Timeout - execução demorou muito")
    except Exception as e:
        execution_status['log'].append(f"❌ Erro: {str(e)}")
    finally:
        execution_status['running'] = False
        execution_status['current_scenario'] = None

if __name__ == '__main__':
    print("🌐 Iniciando Interface Web do Framework Mininet-WiFi")
    print("📱 Acesse: http://localhost:5000")
    print("🛑 Para parar: Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=False) 