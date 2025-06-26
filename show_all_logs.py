#!/usr/bin/env python3
"""
Script para mostrar todos os logs gerados e suas estatísticas
"""
import os
import json
import csv
from datetime import datetime

def analyze_csv_log(filename):
    """Analisa um log CSV"""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        return None
    
    # Estatísticas básicas
    stats = {
        'filename': filename,
        'format': 'CSV',
        'total_records': len(rows),
        'columns': list(rows[0].keys()) if rows else [],
        'first_record': rows[0] if rows else None,
        'last_record': rows[-1] if rows else None
    }
    
    # Análise de RSSI se disponível
    if 'rssi' in rows[0]:
        rssi_values = [float(row['rssi']) for row in rows if row['rssi']]
        stats['rssi_stats'] = {
            'min': min(rssi_values) if rssi_values else None,
            'max': max(rssi_values) if rssi_values else None,
            'avg': sum(rssi_values) / len(rssi_values) if rssi_values else None
        }
    
    # Análise de APs
    if 'ap' in rows[0]:
        ap_counts = {}
        for row in rows:
            ap = row.get('ap', 'unknown')
            ap_counts[ap] = ap_counts.get(ap, 0) + 1
        stats['ap_distribution'] = ap_counts
    
    return stats

def analyze_json_log(filename):
    """Analisa um log JSON"""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    stats = {
        'filename': filename,
        'format': 'JSON',
        'scenario': data.get('scenario', 'Unknown'),
        'description': data.get('description', 'No description'),
        'total_iterations': data.get('total_iterations', 0),
        'total_records': len(data.get('logs', [])),
        'structure': list(data.keys())
    }
    
    # Análise dos logs se disponível
    logs = data.get('logs', [])
    if logs:
        stats['first_record'] = logs[0]
        stats['last_record'] = logs[-1]
        
        # Análise de RSSI
        rssi_values = []
        ap_counts = {}
        
        for log in logs:
            best_ap = log.get('best_ap')
            if best_ap and 'rssi' in best_ap:
                rssi_values.append(best_ap['rssi'])
                ap_name = best_ap.get('name', 'unknown')
                ap_counts[ap_name] = ap_counts.get(ap_name, 0) + 1
        
        if rssi_values:
            stats['rssi_stats'] = {
                'min': min(rssi_values),
                'max': max(rssi_values),
                'avg': sum(rssi_values) / len(rssi_values)
            }
        
        if ap_counts:
            stats['ap_distribution'] = ap_counts
    
    return stats

def main():
    print("📊 ANÁLISE DE TODOS OS LOGS GERADOS")
    print("=" * 50)
    
    # Lista de arquivos de log esperados
    log_files = [
        'rasp_car_scan_log.csv',
        'rasp_car_rout_scan_log.csv', 
        'rasp_car_scan_extended_log.csv',
        'rasp_car_json_log.json'
    ]
    
    all_stats = []
    
    for filename in log_files:
        print(f"\n🔍 Analisando: {filename}")
        print("-" * 30)
        
        if filename.endswith('.csv'):
            stats = analyze_csv_log(filename)
        elif filename.endswith('.json'):
            stats = analyze_json_log(filename)
        else:
            stats = None
        
        if stats:
            all_stats.append(stats)
            print(f"✅ Arquivo encontrado e analisado")
            print(f"   📄 Formato: {stats['format']}")
            print(f"   📊 Registros: {stats['total_records']}")
            
            if 'rssi_stats' in stats:
                rssi = stats['rssi_stats']
                print(f"   📶 RSSI - Min: {rssi['min']:.2f}, Max: {rssi['max']:.2f}, Média: {rssi['avg']:.2f}")
            
            if 'ap_distribution' in stats:
                print(f"   📡 Distribuição de APs:")
                for ap, count in stats['ap_distribution'].items():
                    print(f"      {ap}: {count} registros")
            
            if 'columns' in stats:
                print(f"   📋 Colunas: {', '.join(stats['columns'])}")
            
            if 'scenario' in stats:
                print(f"   🎯 Cenário: {stats['scenario']}")
                print(f"   📝 Descrição: {stats['description']}")
        else:
            print(f"❌ Arquivo não encontrado ou vazio")
    
    # Resumo geral
    print(f"\n📈 RESUMO GERAL")
    print("=" * 50)
    print(f"📁 Total de logs válidos: {len(all_stats)}")
    
    total_records = sum(stats['total_records'] for stats in all_stats)
    print(f"📊 Total de registros: {total_records}")
    
    formats = {}
    for stats in all_stats:
        fmt = stats['format']
        formats[fmt] = formats.get(fmt, 0) + 1
    
    print(f"📄 Formatos: {', '.join([f'{fmt}: {count}' for fmt, count in formats.items()])}")
    
    # Mostrar exemplos de dados
    print(f"\n📋 EXEMPLOS DE DADOS")
    print("=" * 50)
    
    for stats in all_stats:
        print(f"\n📄 {stats['filename']} ({stats['format']}):")
        if 'first_record' in stats and stats['first_record']:
            if stats['format'] == 'CSV':
                print(f"   Primeiro registro: {dict(stats['first_record'])}")
            else:
                # Para JSON, mostrar apenas campos principais
                record = stats['first_record']
                if 'timestamp' in record:
                    print(f"   Timestamp: {record['timestamp']}")
                if 'best_ap' in record:
                    print(f"   Melhor AP: {record['best_ap'].get('name', 'N/A')} (RSSI: {record['best_ap'].get('rssi', 'N/A')})")
                if 'position' in record:
                    pos = record['position']
                    if isinstance(pos, dict):
                        print(f"   Posição: x={pos.get('x', 0)}, y={pos.get('y', 0)}, z={pos.get('z', 0)}")
                    else:
                        print(f"   Posição: {pos}")

if __name__ == '__main__':
    main() 