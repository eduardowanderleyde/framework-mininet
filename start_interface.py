#!/usr/bin/env python3
"""
Script para iniciar a Interface Web do Framework Mininet-WiFi
"""
import os
import sys
import subprocess

def main():
    print("🌐 Framework Mininet-WiFi - Interface Visual")
    print("=" * 50)
    
    # Verificar se o Flask está instalado
    try:
        import flask
        print("✅ Flask instalado")
    except ImportError:
        print("❌ Flask não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask instalado com sucesso!")
    
    # Verificar se os arquivos necessários existem
    required_files = [
        "web_interface.py",
        "templates/index.html"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Arquivo não encontrado: {file}")
            return
    
    print("✅ Todos os arquivos necessários encontrados")
    print("\n🚀 Iniciando interface web...")
    print("📱 Acesse: http://localhost:5000")
    print("🛑 Para parar: Ctrl+C")
    print("-" * 50)
    
    # Executar a interface
    try:
        subprocess.run([sys.executable, "web_interface.py"])
    except KeyboardInterrupt:
        print("\n👋 Interface encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar interface: {e}")

if __name__ == "__main__":
    main() 