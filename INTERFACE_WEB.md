# 🌐 Interface Web - Framework Mininet-WiFi

Interface visual simples e intuitiva para configurar e executar cenários de simulação Wi-Fi mesh.

## 🚀 Como Usar

### 1. Iniciar a Interface
```bash
# Método 1: Script automático (recomendado)
python3 start_interface.py

# Método 2: Direto
python3 web_interface.py
```

### 2. Acessar no Navegador
Abra seu navegador e acesse: **http://localhost:5000**

## 🎯 Funcionalidades

### 📋 Cenários Disponíveis
- **Rasp-Car Scanner**: Raspberry Pi móvel escaneando sinais Wi-Fi
- **Rasp-Car-Rout**: Raspberry Pi + Roteador móvel
- **Rasp-Car Extended**: Versão estendida com mais dados
- **Rasp-Car JSON**: Log em formato JSON estruturado

### ⚡ Execução Visual
1. **Selecione um cenário** clicando no card desejado
2. **Clique em "Executar"** para iniciar a simulação
3. **Acompanhe o progresso** em tempo real
4. **Veja os logs** de execução em tempo real

### 📊 Visualização de Resultados
- **Lista de logs gerados** com informações detalhadas
- **Visualizador de dados** para CSV e JSON
- **Download de logs** para análise externa
- **Estatísticas** de execução

## 🎨 Interface

### Design Responsivo
- ✅ Funciona em desktop, tablet e mobile
- ✅ Design moderno com gradientes
- ✅ Animações suaves
- ✅ Feedback visual em tempo real

### Seções Principais
1. **🎯 Cenários Disponíveis**: Cards com todos os cenários
2. **⚡ Status de Execução**: Barra de progresso e logs
3. **📊 Logs Gerados**: Lista de arquivos criados
4. **📋 Visualizador de Dados**: Visualização dos resultados

## 🔧 Configuração

### Pré-requisitos
- Python 3.7+
- Flask (instalado automaticamente)
- Mininet-WiFi (já configurado)

### Estrutura de Arquivos
```
framework-mininet/
├── web_interface.py          # Servidor Flask
├── start_interface.py        # Script de inicialização
├── templates/
│   └── index.html           # Interface HTML
└── scenarios/               # Cenários disponíveis
```

## 📱 Como Funciona

### Backend (Python/Flask)
- **Servidor web** rodando na porta 5000
- **APIs REST** para comunicação com frontend
- **Execução assíncrona** dos cenários
- **Monitoramento** de status em tempo real

### Frontend (HTML/CSS/JavaScript)
- **Interface responsiva** com design moderno
- **Comunicação AJAX** com o backend
- **Atualizações em tempo real** via polling
- **Visualização de dados** formatada

## 🎯 Exemplo de Uso

### Passo a Passo
1. **Inicie a interface**:
   ```bash
   python3 start_interface.py
   ```

2. **Abra o navegador**:
   ```
   http://localhost:5000
   ```

3. **Selecione um cenário**:
   - Clique em "Rasp-Car Scanner"
   - Clique em "▶️ Executar"

4. **Acompanhe a execução**:
   - Veja a barra de progresso
   - Leia os logs em tempo real
   - Aguarde a conclusão

5. **Visualize os resultados**:
   - Clique em "👁️ Visualizar" nos logs
   - Baixe os arquivos com "⬇️ Download"

## 🔍 APIs Disponíveis

### Executar Cenário
```
POST /api/run_scenario
Body: {"scenario": "rasp_car_scan"}
```

### Status da Execução
```
GET /api/status
Response: {"running": true, "progress": 50, "log": [...]}
```

### Listar Logs
```
GET /api/logs
Response: [{"scenario": "...", "file": "...", "size": 1234}]
```

### Visualizar Log
```
GET /api/view_log/rasp_car_scan_log.csv
Response: {"type": "csv", "lines": [...], "total_lines": 10}
```

### Download Log
```
GET /api/download/rasp_car_scan_log.csv
Response: Arquivo para download
```

## 🛠️ Personalização

### Adicionar Novo Cenário
1. **Crie o arquivo** em `scenarios/`
2. **Adicione à configuração** em `web_interface.py`:
   ```python
   'novo_cenario': {
       'name': 'Nome do Cenário',
       'description': 'Descrição do cenário',
       'file': 'scenarios/novo_cenario.py',
       'log_file': 'novo_cenario_log.csv'
   }
   ```

### Modificar Design
- **CSS**: Edite o `<style>` em `templates/index.html`
- **JavaScript**: Modifique as funções no `<script>`
- **HTML**: Ajuste a estrutura da página

## 🐛 Solução de Problemas

### Interface não carrega
```bash
# Verificar se Flask está instalado
pip3 install flask

# Verificar se porta 5000 está livre
lsof -i :5000
```

### Cenário não executa
```bash
# Verificar permissões
sudo chmod +x scenarios/*.py

# Verificar Mininet-WiFi
python3 -c "import mn_wifi; print('OK')"
```

### Logs não aparecem
```bash
# Verificar permissões dos arquivos
sudo chown $USER:$USER *.csv *.json

# Verificar se arquivos existem
ls -la *.csv *.json
```

## 📈 Próximas Melhorias

### Funcionalidades Planejadas
- [ ] **Gráficos interativos** com Chart.js
- [ ] **Configuração de parâmetros** via interface
- [ ] **Comparação de cenários** lado a lado
- [ ] **Exportação de relatórios** em PDF
- [ ] **Autenticação** de usuários
- [ ] **Histórico de execuções** com banco de dados

### Melhorias Técnicas
- [ ] **WebSockets** para atualizações em tempo real
- [ ] **Cache** de resultados
- [ ] **Compressão** de logs grandes
- [ ] **Validação** de entrada de dados
- [ ] **Logs de erro** mais detalhados

---

**🎉 Interface criada para facilitar o uso do framework!**

Agora você pode executar cenários e visualizar resultados de forma simples e intuitiva, sem precisar usar linha de comando. 