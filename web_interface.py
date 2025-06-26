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
import csv
import pandas as pd
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

@app.route('/api/list_graphs')
def list_graphs():
    """Lista os gráficos de mobilidade gerados (PNG)"""
    png_files = [f for f in os.listdir('.') if f.startswith('mobility_path_') and f.endswith('.png')]
    # Ordenar do mais recente para o mais antigo
    png_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    # Retornar caminhos relativos
    return jsonify({'graphs': png_files})

@app.route('/api/analyze_csv/<filename>')
def analyze_csv(filename):
    """Analisa um arquivo CSV e retorna estatísticas detalhadas"""
    if not os.path.exists(filename):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        # Ler o CSV
        df = pd.read_csv(filename)
        
        # Estatísticas básicas
        stats = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'file_size': os.path.getsize(filename),
            'last_modified': datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Análise por coluna
        column_analysis = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                column_analysis[col] = {
                    'type': 'numeric',
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
            else:
                column_analysis[col] = {
                    'type': 'categorical',
                    'unique_values': int(df[col].nunique()),
                    'most_common': df[col].value_counts().head(3).to_dict()
                }
        
        stats['column_analysis'] = column_analysis
        
        # Análise específica para logs de rede
        if 'rssi' in df.columns:
            stats['rssi_analysis'] = {
                'min_rssi': float(df['rssi'].min()),
                'max_rssi': float(df['rssi'].max()),
                'avg_rssi': float(df['rssi'].mean()),
                'rssi_range': float(df['rssi'].max() - df['rssi'].min())
            }
        
        if 'distance' in df.columns:
            stats['distance_analysis'] = {
                'min_distance': float(df['distance'].min()),
                'max_distance': float(df['distance'].max()),
                'avg_distance': float(df['distance'].mean()),
                'total_distance_covered': float(df['distance'].sum())
            }
        
        if 'ap' in df.columns:
            stats['ap_analysis'] = {
                'unique_aps': int(df['ap'].nunique()),
                'ap_counts': df['ap'].value_counts().to_dict(),
                'most_used_ap': df['ap'].mode().iloc[0] if not df['ap'].mode().empty else None
            }
        
        # Amostra dos dados (primeiras 10 linhas)
        stats['sample_data'] = df.head(10).to_dict('records')
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao analisar CSV: {str(e)}'}), 500

@app.route('/api/view_csv_data/<filename>')
def view_csv_data(filename):
    """Visualiza dados CSV com paginação"""
    if not os.path.exists(filename):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Ler o CSV
        df = pd.read_csv(filename)
        
        # Calcular paginação
        total_rows = len(df)
        total_pages = (total_rows + per_page - 1) // per_page
        
        # Obter dados da página
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_data = df.iloc[start_idx:end_idx]
        
        return jsonify({
            'data': page_data.to_dict('records'),
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'per_page': per_page,
                'total_rows': total_rows,
                'start_row': start_idx + 1,
                'end_row': min(end_idx, total_rows)
            },
            'columns': list(df.columns)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao visualizar dados: {str(e)}'}), 500

@app.route('/api/search_csv/<filename>')
def search_csv(filename):
    """Busca em dados CSV"""
    if not os.path.exists(filename):
        return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    try:
        query = request.args.get('q', '')
        column = request.args.get('column', '')
        
        if not query:
            return jsonify({'error': 'Query de busca é obrigatória'}), 400
        
        # Ler o CSV
        df = pd.read_csv(filename)
        
        # Fazer busca
        if column and column in df.columns:
            # Busca em coluna específica
            mask = df[column].astype(str).str.contains(query, case=False, na=False)
        else:
            # Busca em todas as colunas
            mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
        
        results = df[mask]
        
        return jsonify({
            'results': results.to_dict('records'),
            'total_found': len(results),
            'query': query,
            'column': column
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na busca: {str(e)}'}), 500

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

def get_scenarios():
    """Retorna lista de cenários disponíveis"""
    return [
        {
            'id': 'basic',
            'name': 'Cenário Básico Wi-Fi',
            'file': 'scenarios/basic_wifi.py',
            'description': 'Cenário básico Wi-Fi com AP e estações'
        },
        {
            'id': 'mesh',
            'name': 'Rede Mesh com Mobilidade',
            'file': 'scenarios/mesh_mobility.py',
            'description': 'Rede mesh com mobilidade'
        },
        {
            'id': 'interference',
            'name': 'Teste de Interferência',
            'file': 'scenarios/interference_test.py',
            'description': 'Teste de interferência entre APs'
        },
        {
            'id': 'sdn',
            'name': 'Validação SDN',
            'file': 'scenarios/sdn_wifi_test.py',
            'description': 'Validação SDN com Wi-Fi'
        },
        {
            'id': 'rasp-car',
            'name': 'Raspberry Pi Scanner',
            'file': 'scenarios/rasp_car_scan.py',
            'description': 'Raspberry Pi móvel escaneando rede mesh'
        },
        {
            'id': 'rasp-car-rout',
            'name': 'Raspberry Pi + Roteador Móvel',
            'file': 'scenarios/rasp_car_rout_scan.py',
            'description': 'Raspberry Pi + roteador móvel em carrinho'
        },
        {
            'id': 'mastering-1',
            'name': '🎯 Mastering Scenario 1',
            'file': 'scenarios/mastering-scenario-1.py',
            'description': '3 roteadores mesh + Raspberry Pi móvel em carrinho'
        }
    ]

if __name__ == '__main__':
    print("🌐 Iniciando Interface Web do Framework Mininet-WiFi")
    print("📱 Acesse: http://localhost:5000")
    print("🛑 Para parar: Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=False) 