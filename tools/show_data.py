#!/usr/bin/env python3
"""
Visualizador de Dados - Framework Mininet-WiFi
==============================================

Ferramenta amigável para visualizar e analisar logs CSV dos cenários:
- Resumo rápido dos dados
- Visualização em tabela
- Estatísticas principais
- Comparação entre cenários

Autor: Framework Mininet-WiFi
Data: 2024
"""

import pandas as pd
import argparse
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class DataViewer:
    """Classe para visualizar dados dos logs CSV de forma amigável"""
    
    def __init__(self):
        self.logs = {}
        self.find_logs()
    
    def find_logs(self):
        """Encontra todos os logs CSV disponíveis"""
        csv_files = glob.glob("*.csv")
        for file in csv_files:
            if file.endswith('.csv'):
                self.logs[file] = file
        print(f"📁 Encontrados {len(self.logs)} arquivos de log")
    
    def show_available_logs(self):
        """Mostra logs disponíveis"""
        print("\n📋 LOGS DISPONÍVEIS:")
        print("=" * 50)
        
        if not self.logs:
            print("❌ Nenhum log encontrado!")
            print("💡 Execute um cenário primeiro para gerar logs")
            return
        
        for i, (name, file) in enumerate(self.logs.items(), 1):
            try:
                df = pd.read_csv(file)
                size = os.path.getsize(file)
                records = len(df)
                print(f"{i}. 📄 {name}")
                print(f"   📊 {records} registros | 📏 {size} bytes")
                
                # Mostrar período de tempo se disponível
                if 'timestamp' in df.columns and len(df) > 0:
                    start_time = datetime.fromtimestamp(df['timestamp'].iloc[0])
                    end_time = datetime.fromtimestamp(df['timestamp'].iloc[-1])
                    duration = end_time - start_time
                    print(f"   ⏰ {start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')} ({duration.total_seconds():.1f}s)")
                
                # Mostrar APs utilizados
                if 'ap' in df.columns:
                    aps = df['ap'].unique()
                    print(f"   📡 APs: {', '.join(aps)}")
                
                print()
                
            except Exception as e:
                print(f"{i}. ❌ {name} (erro: {e})")
    
    def load_log(self, log_file):
        """Carrega um log específico"""
        try:
            df = pd.read_csv(log_file)
            print(f"✅ Log carregado: {log_file}")
            print(f"📊 {len(df)} registros encontrados")
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar {log_file}: {e}")
            return None
    
    def show_summary(self, log_file):
        """Mostra resumo rápido do log"""
        df = self.load_log(log_file)
        if df is None:
            return
        
        print(f"\n📊 RESUMO: {log_file}")
        print("=" * 60)
        
        # Informações básicas
        print(f"📈 Total de registros: {len(df)}")
        print(f"📅 Período: {datetime.fromtimestamp(df['timestamp'].iloc[0]).strftime('%d/%m/%Y %H:%M:%S')} - {datetime.fromtimestamp(df['timestamp'].iloc[-1]).strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Estatísticas de RSSI
        if 'rssi' in df.columns:
            print(f"\n📶 RSSI:")
            print(f"   🟢 Melhor: {df['rssi'].max():.1f} dBm")
            print(f"   🔴 Pior: {df['rssi'].min():.1f} dBm")
            print(f"   📊 Média: {df['rssi'].mean():.1f} dBm")
        
        # Estatísticas de distância
        if 'distance' in df.columns:
            print(f"\n📏 Distância:")
            print(f"   🏠 Mais próxima: {df['distance'].min():.1f} m")
            print(f"   🏃 Mais distante: {df['distance'].max():.1f} m")
            print(f"   📊 Média: {df['distance'].mean():.1f} m")
        
        # Estatísticas de latência
        if 'latency' in df.columns:
            print(f"\n⏱️  Latência:")
            print(f"   ⚡ Menor: {df['latency'].min():.1f} ms")
            print(f"   🐌 Maior: {df['latency'].max():.1f} ms")
            print(f"   📊 Média: {df['latency'].mean():.1f} ms")
        
        # Análise de conectividade
        if 'connected' in df.columns:
            connected = len(df[df['connected'] == 'YES'])
            total = len(df)
            rate = (connected / total) * 100
            print(f"\n🔗 Conectividade:")
            print(f"   🟢 Conectado: {connected}/{total} ({rate:.1f}%)")
            print(f"   🔴 Desconectado: {total-connected}/{total} ({100-rate:.1f}%)")
        
        # Análise por AP
        if 'ap' in df.columns:
            print(f"\n📡 Performance por AP:")
            ap_stats = df.groupby('ap').agg({
                'rssi': ['mean', 'count'],
                'distance': 'mean',
                'latency': 'mean'
            }).round(2)
            
            for ap in df['ap'].unique():
                ap_data = df[df['ap'] == ap]
                rssi_mean = ap_data['rssi'].mean()
                count = len(ap_data)
                distance_mean = ap_data['distance'].mean()
                
                # Ícone de qualidade baseado no RSSI
                if rssi_mean > -50:
                    quality = "🟢 Excelente"
                elif rssi_mean > -60:
                    quality = "🟡 Boa"
                elif rssi_mean > -70:
                    quality = "🟠 Regular"
                else:
                    quality = "🔴 Ruim"
                
                print(f"   📶 {ap}: {rssi_mean:.1f} dBm ({quality}) | {count} scans | {distance_mean:.1f}m")
    
    def show_table(self, log_file, limit=10):
        """Mostra dados em formato de tabela"""
        df = self.load_log(log_file)
        if df is None:
            return
        
        print(f"\n📋 DADOS EM TABELA: {log_file}")
        print("=" * 80)
        
        # Selecionar colunas relevantes
        columns_to_show = ['timestamp', 'position', 'ap', 'rssi', 'distance', 'latency', 'connected']
        available_columns = [col for col in columns_to_show if col in df.columns]
        
        if not available_columns:
            print("❌ Nenhuma coluna relevante encontrada")
            return
        
        # Mostrar primeiras linhas
        display_df = df[available_columns].head(limit)
        
        # Formatar timestamp
        if 'timestamp' in display_df.columns:
            display_df['timestamp'] = display_df['timestamp'].apply(
                lambda x: datetime.fromtimestamp(x).strftime('%H:%M:%S')
            )
        
        # Formatar RSSI com cores
        if 'rssi' in display_df.columns:
            def format_rssi(rssi):
                if rssi > -50:
                    return f"🟢 {rssi:.1f}"
                elif rssi > -60:
                    return f"🟡 {rssi:.1f}"
                elif rssi > -70:
                    return f"🟠 {rssi:.1f}"
                else:
                    return f"🔴 {rssi:.1f}"
            
            display_df['rssi'] = display_df['rssi'].apply(format_rssi)
        
        # Formatar conectividade
        if 'connected' in display_df.columns:
            display_df['connected'] = display_df['connected'].apply(
                lambda x: "🟢 SIM" if x == 'YES' else "🔴 NÃO"
            )
        
        print(display_df.to_string(index=False))
        
        if len(df) > limit:
            print(f"\n... e mais {len(df) - limit} registros")
    
    def compare_logs(self, log1, log2):
        """Compara dois logs"""
        df1 = self.load_log(log1)
        df2 = self.load_log(log2)
        
        if df1 is None or df2 is None:
            return
        
        print(f"\n🔄 COMPARAÇÃO: {log1} vs {log2}")
        print("=" * 60)
        
        # Comparar RSSI médio
        if 'rssi' in df1.columns and 'rssi' in df2.columns:
            rssi1 = df1['rssi'].mean()
            rssi2 = df2['rssi'].mean()
            diff = rssi2 - rssi1
            
            print(f"📶 RSSI Médio:")
            print(f"   {log1}: {rssi1:.1f} dBm")
            print(f"   {log2}: {rssi2:.1f} dBm")
            print(f"   📊 Diferença: {diff:+.1f} dBm")
        
        # Comparar conectividade
        if 'connected' in df1.columns and 'connected' in df2.columns:
            conn1 = len(df1[df1['connected'] == 'YES']) / len(df1) * 100
            conn2 = len(df2[df2['connected'] == 'YES']) / len(df2) * 100
            
            print(f"\n🔗 Taxa de Conectividade:")
            print(f"   {log1}: {conn1:.1f}%")
            print(f"   {log2}: {conn2:.1f}%")
            print(f"   📊 Diferença: {conn2-conn1:+.1f}%")
        
        # Comparar latência
        if 'latency' in df1.columns and 'latency' in df2.columns:
            lat1 = df1['latency'].mean()
            lat2 = df2['latency'].mean()
            
            print(f"\n⏱️  Latência Média:")
            print(f"   {log1}: {lat1:.1f} ms")
            print(f"   {log2}: {lat2:.1f} ms")
            print(f"   📊 Diferença: {lat2-lat1:+.1f} ms")
    
    def show_quick_stats(self):
        """Mostra estatísticas rápidas de todos os logs"""
        print("\n📊 ESTATÍSTICAS RÁPIDAS DE TODOS OS LOGS")
        print("=" * 60)
        
        if not self.logs:
            print("❌ Nenhum log encontrado!")
            return
        
        for log_file in self.logs:
            df = self.load_log(log_file)
            if df is None:
                continue
            
            print(f"\n📄 {log_file}:")
            print(f"   📊 {len(df)} registros")
            
            if 'rssi' in df.columns:
                print(f"   📶 RSSI: {df['rssi'].mean():.1f} dBm (médio)")
            
            if 'connected' in df.columns:
                connected = len(df[df['connected'] == 'YES'])
                rate = (connected / len(df)) * 100
                print(f"   🔗 Conectividade: {rate:.1f}%")
            
            if 'ap' in df.columns:
                aps = df['ap'].unique()
                print(f"   📡 APs utilizados: {len(aps)}")
    
    def interactive_menu(self):
        """Menu interativo para o usuário"""
        while True:
            print("\n🎯 VISUALIZADOR DE DADOS - Framework Mininet-WiFi")
            print("=" * 60)
            print("1. 📋 Ver logs disponíveis")
            print("2. 📊 Resumo de um log")
            print("3. 📋 Ver dados em tabela")
            print("4. 🔄 Comparar dois logs")
            print("5. 📈 Estatísticas rápidas")
            print("6. 🚪 Sair")
            
            choice = input("\nEscolha uma opção (1-6): ").strip()
            
            if choice == '1':
                self.show_available_logs()
            
            elif choice == '2':
                self.show_available_logs()
                if self.logs:
                    log_choice = input("\nDigite o nome do log para analisar: ").strip()
                    if log_choice in self.logs:
                        self.show_summary(log_choice)
                    else:
                        print("❌ Log não encontrado!")
            
            elif choice == '3':
                self.show_available_logs()
                if self.logs:
                    log_choice = input("\nDigite o nome do log para visualizar: ").strip()
                    if log_choice in self.logs:
                        limit = input("Quantos registros mostrar? (padrão: 10): ").strip()
                        limit = int(limit) if limit.isdigit() else 10
                        self.show_table(log_choice, limit)
                    else:
                        print("❌ Log não encontrado!")
            
            elif choice == '4':
                self.show_available_logs()
                if len(self.logs) >= 2:
                    log1 = input("\nDigite o nome do primeiro log: ").strip()
                    log2 = input("Digite o nome do segundo log: ").strip()
                    
                    if log1 in self.logs and log2 in self.logs:
                        self.compare_logs(log1, log2)
                    else:
                        print("❌ Um ou ambos os logs não encontrados!")
                else:
                    print("❌ Precisa de pelo menos 2 logs para comparar!")
            
            elif choice == '5':
                self.show_quick_stats()
            
            elif choice == '6':
                print("👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida!")


def main():
    parser = argparse.ArgumentParser(description='Visualizar dados dos logs CSV')
    parser.add_argument('--interactive', '-i', action='store_true', help='Modo interativo')
    parser.add_argument('--log', help='Log específico para analisar')
    parser.add_argument('--summary', action='store_true', help='Mostrar resumo')
    parser.add_argument('--table', action='store_true', help='Mostrar tabela')
    parser.add_argument('--compare', nargs=2, help='Comparar dois logs')
    parser.add_argument('--quick', action='store_true', help='Estatísticas rápidas')
    
    args = parser.parse_args()
    
    viewer = DataViewer()
    
    if args.interactive:
        viewer.interactive_menu()
    elif args.log:
        if args.summary:
            viewer.show_summary(args.log)
        elif args.table:
            viewer.show_table(args.log)
        else:
            viewer.show_summary(args.log)
    elif args.compare:
        viewer.compare_logs(args.compare[0], args.compare[1])
    elif args.quick:
        viewer.show_quick_stats()
    else:
        # Modo padrão: mostrar logs disponíveis
        viewer.show_available_logs()


if __name__ == '__main__':
    main() 