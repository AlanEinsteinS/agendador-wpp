# WhatsApp Scheduler Pro

![WhatsApp Scheduler](https://img.shields.io/badge/WhatsApp-Scheduler-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-Automation-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

Um agendador de mensagens automático para WhatsApp que permite programar o envio de mensagens para qualquer horário futuro, com envio totalmente automatizado sem necessidade de intervenção manual.

## ✨ Funcionalidades

- 📝 Agende mensagens para qualquer contato ou grupo do WhatsApp
- ⏰ Defina data e hora específicas para envio automático
- 🤖 Envio totalmente automatizado (sem necessidade de clicar "Enviar")
- ✏️ Edite mensagens e horários de agendamento
- 🗑️ Sistema avançado de exclusão (individual ou em lote)
- 📋 Duplicação rápida de mensagens
- 💾 Armazenamento local das mensagens agendadas
- 📊 Interface gráfica intuitiva para gerenciamento de mensagens
- 🔄 Verifica status da conexão com WhatsApp Web
- 🚀 Permite envio de mensagens de teste

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Google Chrome instalado
- Conexão com a internet
- WhatsApp ativo em seu telefone

## 🛠️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/AlanEinsteinS/agendador-wpp/.git
   cd agendador-wpp
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   python whatsapp_scheduler.py
   ```

## 📱 Como usar

### Configuração inicial
1. Na primeira execução, escaneie o código QR com seu WhatsApp móvel
2. Aguarde a conexão ser estabelecida (status "Conectado")

### Agendando mensagens
1. Preencha o número do destinatário com código do país (ex: 5511999999999)
2. Digite a mensagem a ser enviada
3. Defina a data (DD/MM/AAAA) e hora (HH:MM)
4. Clique em "Agendar Mensagem"

### Gerenciando o agendador
1. Clique em "Iniciar Agendador" para começar o monitoramento
2. O sistema enviará automaticamente as mensagens nos horários programados
3. Use "Verificar Status WhatsApp" para garantir que a conexão está ativa

### Editando e gerenciando mensagens
1. Selecione uma mensagem na lista e clique em "Editar Selecionado" para modificar o conteúdo
2. Use "Reagendar" para alterar a data e hora de envio de uma mensagem
3. Utilize "Duplicar" para criar uma cópia de uma mensagem existente
4. Selecione e exclua mensagens individualmente ou use as opções avançadas de exclusão:
   - Excluir todas as mensagens
   - Excluir apenas mensagens já enviadas
   - Excluir apenas mensagens com erro
   - Excluir mensagens mais antigas que uma semana

## 🖥️ Criando um executável

Você pode converter o agendador em um arquivo executável (.exe) para facilitar o uso e distribuição:

### Instalando PyInstaller
```bash
pip install pyinstaller
```

### Resolvendo problemas de PATH
Se o PyInstaller não for reconhecido, use uma destas alternativas:

1. Use o comando Python para executar o PyInstaller:
   ```bash
   python -m PyInstaller --name "Agendador WhatsApp" --windowed --onefile whatsapp_scheduler.py
   ```

2. Ou crie um script Python para a compilação (build_app.py):
   ```python
   import os
   import sys
   import subprocess

   # Instala PyInstaller se necessário
   try:
       import PyInstaller
   except ImportError:
       print("Instalando PyInstaller...")
       subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

   # Executa o PyInstaller 
   print("Criando executável...")
   subprocess.check_call([
       sys.executable, 
       "-m", 
       "PyInstaller", 
       "--name", 
       "Agendador WhatsApp", 
       "--windowed", 
       "--onefile", 
       "whatsapp_scheduler.py"
   ])

   print("Executável criado com sucesso!")
   ```

3. Execute com:
   ```bash
   python build_app.py
   ```

### Adicionando um ícone personalizado

1. Baixe um ícone em formato .ico ou converta um SVG/PNG para .ico
2. Coloque o arquivo "whatsapp_icon.ico" na mesma pasta do script
3. Adicione a flag de ícone ao comando:
   ```bash
   python -m PyInstaller --name "Agendador WhatsApp" --windowed --onefile --icon=whatsapp_icon.ico whatsapp_scheduler.py
   ```

### Observações sobre o executável
- O arquivo .exe estará na pasta "dist" após a compilação
- O tamanho será grande (100-200MB) pois inclui Python e todas as dependências
- A primeira execução pode ser mais lenta
- O Chrome WebDriver será baixado na primeira execução

## 🔍 Demonstração

![Screenshot da aplicação](https://media.discordapp.net/attachments/1316773615110197278/1346749840402546719/5497E6D4-D957-45DB-86B3-6E4236060323.png?ex=67c95207&is=67c80087&hm=765b01992bc5baf4f609c076fced43f2caf6f1165f2ff26c8c78a892f39d6419&=&format=webp&quality=lossless&width=674&height=701)

## ⚠️ Considerações importantes

- O computador precisa estar ligado e o programa em execução no horário agendado
- Não feche o navegador Chrome que é aberto pelo programa
- Mantenha o WhatsApp do celular conectado à internet
- O uso intensivo desta ferramenta pode levar a limitações temporárias no WhatsApp
- Esta ferramenta é apenas para uso pessoal legítimo

## 🐞 Solução de problemas

| Problema | Solução |
|----------|---------|
| Erro no ChromeDriver | Reinstale o selenium ou baixe o ChromeDriver compatível com sua versão do Chrome |
| WhatsApp não conecta | Verifique sua conexão com a internet e se o WhatsApp no celular está online |
| Mensagens não enviadas | Verifique o formato do número de telefone e se o programa está com status "Conectado" |
| Aplicação travada | Reinicie o programa e tente novamente |
| Botões não aparecem | Aumente o tamanho da janela ou verifique se a resolução da tela é suficiente |
