#!/bin/bash
# Script de Instalação do Mininet-WiFi
# Autor: Framework Mininet-WiFi
# Data: 2024

set -e

echo "🚀 Iniciando instalação do Mininet-WiFi..."

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (sudo)"
    exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "📦 Instalando dependências..."
apt install -y git python3-pip build-essential libnl-3-dev libnl-genl-3-dev
apt install -y pkg-config libssl-dev ethtool rfkill wireless-tools
apt install -y wpasupplicant hostapd wmediumd

# Clonar Mininet-WiFi
echo "📥 Clonando Mininet-WiFi..."
cd /opt
git clone https://github.com/intrig-unicamp/mininet-wifi.git
cd mininet-wifi

# Instalar Mininet-WiFi
echo "🔧 Instalando Mininet-WiFi..."
util/install.sh -Wlnfv

# Verificar instalação
echo "✅ Verificando instalação..."
mn --wifi --test pingall

echo "🎉 Mininet-WiFi instalado com sucesso!"
echo "📁 Diretório: /opt/mininet-wifi"
echo "🚀 Para testar: sudo mn --wifi --test pingall" 