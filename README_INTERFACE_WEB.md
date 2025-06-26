# 🌐 Interface Web - Framework Mininet-WiFi

## 📋 Visão Geral

Esta interface web foi desenvolvida especificamente para o **Caso de Estudo do Mestrado em Redes de Computadores**, focando na análise de mobilidade e performance em redes Wi-Fi mesh.

## 🎯 Objetivo da Pesquisa

O trabalho investiga o comportamento de redes Wi-Fi mesh em cenários de mobilidade, utilizando um carrinho robótico equipado com Raspberry Pi para simular dispositivos móveis em ambientes com múltiplos access points.

## 🚀 Como Executar

### Pré-requisitos
```bash
pip3 install flask pandas matplotlib seaborn numpy
```

### Iniciar a Interface
```bash
# Opção 1: Usando o script de inicialização
python3 start_interface.py

# Opção 2: Executar diretamente
export MPLCONFIGDIR=/tmp && python3 web_interface.py
```

### Acessar a Interface
Abra seu navegador e acesse: **http://localhost:5000**

## 📊 Funcionalidades da Interface

### 1. 🎓 Seção do Mestrado
- **Objetivo da Pesquisa**: Explicação detalhada do trabalho
- **Metodologia**: Descrição dos cenários experimentais
- **Hipótese Principal**: Redes mesh vs redes Wi-Fi tradicionais
- **Resultados Principais**: Estatísticas calculadas em tempo real
- **Principais Descobertas**: Pontos positivos e desafios identificados

### 2. 📈 Estatísticas em Tempo Real
- **RSSI Médio**: Calculado a partir dos logs CSV
- **Distância**: Mínima e máxima registrada
- **Latência**: Média das medições
- **Conectividade**: Taxa de sucesso das conexões
- **Total de Registros**: Soma de todos os logs

### 3. 🔬 Cenários Experimentais
- **Rasp-Car Scanner**: Raspberry Pi móvel escaneando sinais
- **Rasp-Car-Rout Scanner**: Raspberry Pi + Roteador móvel

### 4. 📋 Visualização de Dados
- **Logs CSV**: Análise detalhada com estatísticas
- **Gráficos**: Visualizações de RSSI, performance e mobilidade
- **Tabelas**: Dados formatados e paginados

## 📁 Estrutura dos Dados

### Logs CSV Gerados
- `rasp_car_scan_log.csv`: Dados do cenário básico
- `rasp_car_rout_scan_log.csv`: Dados do cenário com roteador
- `rasp_car_scan_extended_log.csv`: Dados estendidos

### Gráficos Gerados
- `rssi_over_time_*.png`: RSSI ao longo do tempo
- `ap_performance_*.png`: Performance por access point
- `mobility_path_*.png`: Caminho de mobilidade

## 🔍 Análise dos Resultados

### Métricas Coletadas
1. **RSSI (Received Signal Strength Indicator)**
   - Mede a força do sinal recebido
   - Valores típicos: -30 a -90 dBm

2. **Distância**
   - Distância entre dispositivo e access point
   - Calculada usando triangulação

3. **Latência**
   - Tempo de resposta da rede
   - Medida em milissegundos

4. **Conectividade**
   - Taxa de sucesso das conexões
   - Percentual de tempo conectado

### Principais Descobertas

#### ✅ Pontos Positivos
- Handoff suave entre APs
- Baixa latência de rede
- Cobertura ampla e estável
- Escalabilidade da solução

#### ⚠️ Desafios Identificados
- Variação de RSSI em movimento
- Interferência entre canais
- Complexidade de configuração
- Consumo de energia elevado

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Análise de Dados**: Pandas, NumPy
- **Visualização**: Matplotlib, Seaborn
- **Simulação**: Mininet-WiFi

## 📱 Como Usar a Interface

### 1. Executar Cenários
1. Clique em "Rasp-Car Scanner" ou "Rasp-Car-Rout Scanner"
2. Aguarde a confirmação no modal
3. A página atualiza automaticamente a cada 30 segundos

### 2. Visualizar Logs
1. Clique em "Visualizar" em qualquer log CSV
2. Veja estatísticas automáticas e gráficos de análise
3. Dados são exibidos em tabela formatada

### 3. Ver Gráficos
1. Clique em "Visualizar" em qualquer gráfico PNG
2. Gráficos são exibidos em tela cheia
3. Opções de download e impressão

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
export MPLCONFIGDIR=/tmp  # Para evitar problemas com matplotlib
export FLASK_ENV=development  # Para modo de desenvolvimento
```

### Personalização
- Modifique `templates/index.html` para alterar o layout
- Edite `web_interface.py` para adicionar novas funcionalidades
- Ajuste os estilos CSS para personalizar a aparência

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se os logs CSV estão no diretório correto
3. Verifique as permissões dos arquivos
4. Consulte os logs do Flask para erros

## 🎓 Contexto Acadêmico

Este trabalho faz parte da dissertação de mestrado em Redes de Computadores, investigando a aplicabilidade de redes mesh em cenários de mobilidade urbana e IoT (Internet of Things).

---

**Desenvolvido para o Mestrado em Redes de Computadores**  
*Análise de Mobilidade e Performance em Redes Wi-Fi Mesh* 