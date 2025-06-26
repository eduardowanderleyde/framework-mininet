#!/usr/bin/env python3
"""
Ferramenta de Análise de Logs CSV
================================

Analisa os logs CSV gerados pelos cenários rasp-car e rasp-car-rout:
- Estatísticas de RSSI
- Análise de conectividade
- Performance por AP
- Gráficos de mobilidade

Autor: Framework Mininet-WiFi
Data: 2024
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
from datetime import datetime


class LogAnalyzer:
    """Classe para analisar logs CSV dos cenários Wi-Fi"""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Carrega dados do arquivo CSV"""
        try:
            self.df = pd.read_csv(self.log_file)
            print(f"✅ Dados carregados: {len(self.df)} registros")
        except Exception as e:
            print(f"❌ Erro ao carregar {self.log_file}: {e}")
            return
    
    def basic_stats(self):
        """Estatísticas básicas dos dados"""
        if self.df is None or len(self.df) == 0:
            print("❌ Nenhum dado para analisar")
            return
        
        print("\n📊 ESTATÍSTICAS BÁSICAS")
        print("=" * 50)
        
        # Estatísticas de RSSI
        if 'rssi' in self.df.columns:
            print(f"RSSI Médio: {self.df['rssi'].mean():.2f} dBm")
            print(f"RSSI Máximo: {self.df['rssi'].max():.2f} dBm")
            print(f"RSSI Mínimo: {self.df['rssi'].min():.2f} dBm")
            print(f"Desvio Padrão RSSI: {self.df['rssi'].std():.2f} dBm")
        
        # Estatísticas de distância
        if 'distance' in self.df.columns:
            print(f"Distância Média: {self.df['distance'].mean():.2f} m")
            print(f"Distância Máxima: {self.df['distance'].max():.2f} m")
            print(f"Distância Mínima: {self.df['distance'].min():.2f} m")
        
        # Estatísticas de latência
        if 'latency' in self.df.columns:
            print(f"Latência Média: {self.df['latency'].mean():.2f} ms")
            print(f"Latência Máxima: {self.df['latency'].max():.2f} ms")
            print(f"Latência Mínima: {self.df['latency'].min():.2f} ms")
        
        # Análise de conectividade
        if 'connected' in self.df.columns:
            connected_count = len(self.df[self.df['connected'] == 'YES'])
            total_count = len(self.df)
            connectivity_rate = (connected_count / total_count) * 100
            print(f"Taxa de Conectividade: {connectivity_rate:.1f}% ({connected_count}/{total_count})")
        
        # Análise por AP
        if 'ap' in self.df.columns:
            print("\n📡 ANÁLISE POR ACCESS POINT")
            print("-" * 30)
            ap_stats = self.df.groupby('ap').agg({
                'rssi': ['mean', 'min', 'max', 'count'],
                'distance': ['mean', 'min', 'max'],
                'latency': ['mean', 'min', 'max']
            }).round(2)
            print(ap_stats)
    
    def plot_rssi_over_time(self, save_plot=True):
        """Gráfico de RSSI ao longo do tempo"""
        if self.df is None or 'rssi' not in self.df.columns:
            print("❌ Dados de RSSI não disponíveis")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.df['rssi'], 'b-', linewidth=2, label='RSSI')
        plt.axhline(y=-70, color='r', linestyle='--', label='Threshold (-70 dBm)')
        plt.xlabel('Tempo (registros)')
        plt.ylabel('RSSI (dBm)')
        plt.title('RSSI ao Longo do Tempo')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_plot:
            plot_file = f"rssi_over_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"📈 Gráfico salvo: {plot_file}")
        
        plt.show()
    
    def plot_ap_performance(self, save_plot=True):
        """Gráfico de performance por AP"""
        if self.df is None or 'ap' not in self.df.columns:
            print("❌ Dados de AP não disponíveis")
            return
        
        ap_means = self.df.groupby('ap')['rssi'].mean().sort_values(ascending=False)
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(ap_means.index, ap_means.values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        plt.xlabel('Access Point')
        plt.ylabel('RSSI Médio (dBm)')
        plt.title('Performance por Access Point')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, ap_means.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{value:.1f}', ha='center', va='bottom')
        
        if save_plot:
            plot_file = f"ap_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"📈 Gráfico salvo: {plot_file}")
        
        plt.show()
    
    def plot_mobility_path(self, save_plot=True):
        """Gráfico do caminho de mobilidade"""
        if self.df is None or 'position' not in self.df.columns:
            print("❌ Dados de posição não disponíveis")
            return
        
        # Extrair coordenadas das posições
        positions = []
        for pos_str in self.df['position']:
            try:
                coords = pos_str.split(',')
                x, y = float(coords[0]), float(coords[1])
                positions.append((x, y))
            except:
                continue
        
        if not positions:
            print("❌ Não foi possível extrair posições válidas")
            return
        
        x_coords, y_coords = zip(*positions)
        
        plt.figure(figsize=(10, 8))
        plt.plot(x_coords, y_coords, 'b-o', linewidth=2, markersize=6, label='Caminho do Raspberry')
        
        # Marcar posições dos APs (baseado nos cenários)
        ap_positions = {
            'modem': (10, 30),
            'mesh1': (40, 30),
            'mesh2': (70, 30)
        }
        
        for ap_name, (x, y) in ap_positions.items():
            plt.plot(x, y, 'r^', markersize=10, label=f'{ap_name}')
            plt.text(x+2, y+2, ap_name, fontsize=12, fontweight='bold')
        
        plt.xlabel('Posição X (m)')
        plt.ylabel('Posição Y (m)')
        plt.title('Caminho de Mobilidade do Raspberry Pi')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        if save_plot:
            plot_file = f"mobility_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"📈 Gráfico salvo: {plot_file}")
        
        plt.show()
    
    def generate_report(self):
        """Gera relatório completo"""
        print(f"\n📋 RELATÓRIO DE ANÁLISE: {self.log_file}")
        print("=" * 60)
        
        self.basic_stats()
        
        # Gerar gráficos
        print("\n📈 GERANDO GRÁFICOS...")
        self.plot_rssi_over_time()
        self.plot_ap_performance()
        self.plot_mobility_path()
        
        print("\n✅ Análise concluída!")


def main():
    parser = argparse.ArgumentParser(description='Analisar logs CSV dos cenários Wi-Fi')
    parser.add_argument('log_file', help='Arquivo CSV para analisar')
    parser.add_argument('--no-plots', action='store_true', help='Não gerar gráficos')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.log_file):
        print(f"❌ Arquivo não encontrado: {args.log_file}")
        return
    
    analyzer = LogAnalyzer(args.log_file)
    analyzer.generate_report()


if __name__ == '__main__':
    main() 