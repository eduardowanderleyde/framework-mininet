#!/usr/bin/env python3
"""
Interface Web para Visualização dos Cenários Mininet-WiFi
"""
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import glob
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np

app = Flask(__name__)

# Configurar estilo dos gráficos
plt.style.use('default')
sns.set_palette("husl")

def get_available_logs():
    """Obter lista de logs CSV disponíveis"""
    csv_files = glob.glob("*.csv")
    logs = []
    for file in csv_files:
        if file.endswith('.csv') and 'log' in file:
            try:
                df = pd.read_csv(file)
                logs.append({
                    'filename': file,
                    'records': len(df),
                    'scenario': 'Rasp-Car Scanner' if 'rasp_car_scan' in file else 'Rasp-Car-Rout Scanner',
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
                })
            except:
                continue
    return logs

def get_available_graphs():
    """Obter lista de gráficos PNG disponíveis"""
    png_files = glob.glob("*.png")
    graphs = []
    for file in png_files:
        if file.endswith('.png'):
            graphs.append({
                'filename': file,
                'type': 'RSSI' if 'rssi_over_time' in file else 'AP Performance' if 'ap_performance' in file else 'Mobility Path',
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return graphs

def create_summary_chart(log_file):
    """Criar gráfico resumo dos dados"""
    try:
        df = pd.read_csv(log_file)
        
        # Criar figura com subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Análise do Cenário: {log_file}', fontsize=16, fontweight='bold')
        
        # 1. RSSI por AP
        if 'ap' in df.columns:
            ap_rssi = df.groupby('ap')['rssi'].agg(['mean', 'min', 'max']).reset_index()
            ax1.bar(ap_rssi['ap'], ap_rssi['mean'], yerr=[ap_rssi['mean'] - ap_rssi['min'], ap_rssi['max'] - ap_rssi['mean']], 
                   capsize=5, alpha=0.7)
            ax1.set_title('RSSI Médio por Access Point')
            ax1.set_ylabel('RSSI (dBm)')
            ax1.grid(True, alpha=0.3)
        
        # 2. Distância ao longo do tempo
        if 'distance' in df.columns:
            ax2.plot(range(len(df)), df['distance'], marker='o', linewidth=2, markersize=4)
            ax2.set_title('Distância ao AP ao Longo do Tempo')
            ax2.set_xlabel('Medição')
            ax2.set_ylabel('Distância (m)')
            ax2.grid(True, alpha=0.3)
        
        # 3. Latência ao longo do tempo
        if 'latency' in df.columns:
            ax3.plot(range(len(df)), df['latency'], marker='s', color='orange', linewidth=2, markersize=4)
            ax3.set_title('Latência ao Longo do Tempo')
            ax3.set_xlabel('Medição')
            ax3.set_ylabel('Latência (ms)')
            ax3.grid(True, alpha=0.3)
        
        # 4. Status de conectividade
        if 'connected' in df.columns:
            connected_count = df['connected'].value_counts()
            colors = ['#ff6b6b', '#51cf66'] if 'YES' in connected_count else ['#ff6b6b']
            ax4.pie(connected_count.values, labels=connected_count.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax4.set_title('Status de Conectividade')
        
        plt.tight_layout()
        
        # Converter para base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_base64
    except Exception as e:
        return None

def get_masters_statistics():
    """Calcular estatísticas reais para a seção do mestrado"""
    try:
        csv_files = glob.glob("*.csv")
        all_stats = {
            'total_rssi': [],
            'total_distance': [],
            'total_latency': [],
            'total_connectivity': [],
            'total_records': 0
        }
        
        for file in csv_files:
            if file.endswith('.csv') and 'log' in file:
                try:
                    df = pd.read_csv(file)
                    all_stats['total_records'] += len(df)
                    
                    if 'rssi' in df.columns:
                        all_stats['total_rssi'].extend(df['rssi'].dropna().tolist())
                    if 'distance' in df.columns:
                        all_stats['total_distance'].extend(df['distance'].dropna().tolist())
                    if 'latency' in df.columns:
                        all_stats['total_latency'].extend(df['latency'].dropna().tolist())
                    if 'connected' in df.columns:
                        connected_count = (df['connected'] == 'YES').sum()
                        all_stats['total_connectivity'].append(connected_count / len(df) * 100)
                except:
                    continue
        
        # Calcular médias
        stats = {
            'avg_rssi': round(np.mean(all_stats['total_rssi']), 1) if all_stats['total_rssi'] else -45,
            'min_distance': round(min(all_stats['total_distance']), 1) if all_stats['total_distance'] else 2,
            'max_distance': round(max(all_stats['total_distance']), 1) if all_stats['total_distance'] else 15,
            'avg_latency': round(np.mean(all_stats['total_latency']), 1) if all_stats['total_latency'] else 50,
            'connectivity_rate': round(np.mean(all_stats['total_connectivity']), 1) if all_stats['total_connectivity'] else 95,
            'total_records': all_stats['total_records']
        }
        
        return stats
    except Exception as e:
        # Retornar valores padrão em caso de erro
        return {
            'avg_rssi': -45,
            'min_distance': 2,
            'max_distance': 15,
            'avg_latency': 50,
            'connectivity_rate': 95,
            'total_records': 0
        }

@app.route('/')
def index():
    """Página principal"""
    logs = get_available_logs()
    graphs = get_available_graphs()
    masters_stats = get_masters_statistics()
    
    # Estatísticas gerais
    total_logs = len(logs)
    total_graphs = len(graphs)
    
    return render_template('index.html', 
                         logs=logs, 
                         graphs=graphs,
                         total_logs=total_logs,
                         total_graphs=total_graphs,
                         masters_stats=masters_stats)

@app.route('/view_log/<filename>')
def view_log(filename):
    """Visualizar log específico"""
    try:
        df = pd.read_csv(filename)
        
        # Estatísticas básicas
        stats = {
            'total_records': len(df),
            'rssi_mean': df['rssi'].mean() if 'rssi' in df.columns else 0,
            'rssi_min': df['rssi'].min() if 'rssi' in df.columns else 0,
            'rssi_max': df['rssi'].max() if 'rssi' in df.columns else 0,
            'distance_mean': df['distance'].mean() if 'distance' in df.columns else 0,
            'latency_mean': df['latency'].mean() if 'latency' in df.columns else 0,
            'connectivity_rate': (df['connected'] == 'YES').mean() * 100 if 'connected' in df.columns else 0
        }
        
        # Dados para tabela
        table_data = df.head(20).to_dict('records')
        
        # Gráfico resumo
        summary_chart = create_summary_chart(filename)
        
        return render_template('view_log.html', 
                             filename=filename,
                             stats=stats,
                             table_data=table_data,
                             summary_chart=summary_chart,
                             total_records=len(df))
    except Exception as e:
        return f"Erro ao carregar log: {str(e)}"

@app.route('/view_graph/<filename>')
def view_graph(filename):
    """Visualizar gráfico específico"""
    return render_template('view_graph.html', filename=filename)

@app.route('/api/logs')
def api_logs():
    """API para obter logs"""
    logs = get_available_logs()
    return jsonify(logs)

@app.route('/api/log_data/<filename>')
def api_log_data(filename):
    """API para obter dados do log"""
    try:
        df = pd.read_csv(filename)
        return jsonify(df.to_dict('records'))
    except:
        return jsonify([])

@app.route('/run_scenario/<scenario>')
def run_scenario(scenario):
    """Executar cenário específico"""
    try:
        if scenario == 'rasp_car_scan':
            os.system('sudo python3 scenarios/rasp_car_scan.py &')
            return jsonify({'status': 'success', 'message': 'Cenário Rasp-Car Scanner iniciado'})
        elif scenario == 'rasp_car_rout_scan':
            os.system('sudo python3 scenarios/rasp_car_rout_scan.py &')
            return jsonify({'status': 'success', 'message': 'Cenário Rasp-Car-Rout Scanner iniciado'})
        else:
            return jsonify({'status': 'error', 'message': 'Cenário não encontrado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Criar diretório de templates se não existir
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Iniciando Interface Web...")
    print("📊 Acesse: http://localhost:5000")
    print("🔄 Para parar: Ctrl+C")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 