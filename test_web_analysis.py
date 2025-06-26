#!/usr/bin/env python3
"""
Teste das Funcionalidades de Análise de CSV na Interface Web
===========================================================
Script para testar as novas funcionalidades de análise e visualização de dados CSV
"""
import requests
import json
import time

def test_web_analysis():
    """Testa as funcionalidades de análise de CSV"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testando Funcionalidades de Análise de CSV na Interface Web")
    print("=" * 60)
    
    try:
        # 1. Testar listagem de logs
        print("1️⃣ Testando listagem de logs...")
        response = requests.get(f"{base_url}/api/logs")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Logs encontrados: {len(logs)}")
            for log in logs:
                print(f"   📄 {log['file']} ({log['format']}) - {log['size']} bytes")
        else:
            print(f"❌ Erro ao listar logs: {response.status_code}")
            return
        
        # 2. Testar análise de CSV
        csv_logs = [log for log in logs if log['format'] == 'CSV']
        if csv_logs:
            test_file = csv_logs[0]['file']
            print(f"\n2️⃣ Testando análise de CSV: {test_file}")
            
            response = requests.get(f"{base_url}/api/analyze_csv/{test_file}")
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Análise realizada com sucesso!")
                print(f"   📈 Total de linhas: {analysis['total_rows']}")
                print(f"   📄 Tamanho: {analysis['file_size']} bytes")
                
                if 'rssi_analysis' in analysis:
                    rssi = analysis['rssi_analysis']
                    print(f"   📶 RSSI - Min: {rssi['min_rssi']:.2f}, Max: {rssi['max_rssi']:.2f}, Média: {rssi['avg_rssi']:.2f}")
                
                if 'distance_analysis' in analysis:
                    dist = analysis['distance_analysis']
                    print(f"   📏 Distância - Min: {dist['min_distance']:.2f}m, Max: {dist['max_distance']:.2f}m")
                
                if 'ap_analysis' in analysis:
                    ap = analysis['ap_analysis']
                    print(f"   🌐 APs únicos: {ap['unique_aps']}")
            else:
                print(f"❌ Erro na análise: {response.status_code}")
        
        # 3. Testar visualização de dados CSV
        if csv_logs:
            test_file = csv_logs[0]['file']
            print(f"\n3️⃣ Testando visualização de dados CSV: {test_file}")
            
            response = requests.get(f"{base_url}/api/view_csv_data/{test_file}?page=1&per_page=10")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Visualização realizada com sucesso!")
                print(f"   📋 Página {data['pagination']['current_page']} de {data['pagination']['total_pages']}")
                print(f"   📊 Linhas: {data['pagination']['start_row']}-{data['pagination']['end_row']} de {data['pagination']['total_rows']}")
                print(f"   📋 Colunas: {', '.join(data['columns'])}")
                
                if data['data']:
                    print(f"   📄 Primeira linha: {data['data'][0]}")
            else:
                print(f"❌ Erro na visualização: {response.status_code}")
        
        # 4. Testar busca em CSV
        if csv_logs:
            test_file = csv_logs[0]['file']
            print(f"\n4️⃣ Testando busca em CSV: {test_file}")
            
            response = requests.get(f"{base_url}/api/search_csv/{test_file}?q=modem")
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ Busca realizada com sucesso!")
                print(f"   🔍 Resultados encontrados: {search_results['total_found']}")
                print(f"   🔍 Query: '{search_results['query']}'")
            else:
                print(f"❌ Erro na busca: {response.status_code}")
        
        print("\n🎉 Todos os testes concluídos!")
        print("\n🌐 Acesse a interface web em: http://localhost:5000")
        print("📊 Use os botões '📊 Analisar' e '📋 Ver Dados' nos logs CSV")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Interface web não está rodando!")
        print("💡 Execute: python3 start_interface.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_web_analysis() 