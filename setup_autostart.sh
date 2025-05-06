#!/bin/bash

# HAB Project - Autostart Setup Script
# This script sets up the HAB Project to start automatically on boot

echo "===== HAB Project - Autostart Setup ====="

# Get the current username
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

# Pergunte se o usuário deseja rodar com ou sem Arduino
read -p "Deseja usar o Arduino? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ARDUINO_FLAG=""
else
    ARDUINO_FLAG="--no-arduino"
fi

# Pergunte se o usuário deseja reconhecimento de voz
read -p "Ativar reconhecimento de voz? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    VOICE_FLAG=""
    # Adicione o usuário ao grupo de áudio
    sudo usermod -a -G audio $CURRENT_USER
    echo "Adicionado ao grupo de áudio. Será necessário fazer logout/login para que tenha efeito."
else
    VOICE_FLAG="--no-voice"
fi

# Check if we want to run in headless mode
read -p "Executar em modo headless (sem interface gráfica)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    HEADLESS_FLAG="--headless"
else
    HEADLESS_FLAG=""
    # Certifique-se de ter as bibliotecas necessárias para GUI
    sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
    pip install opencv-python
fi

# Pergunte se o usuário deseja ver a saída no terminal
read -p "Deseja ver a saída no terminal (recomendado para debug)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    TERMINAL_OUTPUT=true
else
    TERMINAL_OUTPUT=false
fi

# Defina todos os argumentos
ARGS="$ARDUINO_FLAG $VOICE_FLAG $HEADLESS_FLAG"

# Adicione quaisquer argumentos de linha de comando adicionais
read -p "Adicione quaisquer argumentos adicionais de linha de comando (exemplo: --low-power): " EXTRA_ARGS
if [ ! -z "$EXTRA_ARGS" ]; then
    ARGS="$ARGS $EXTRA_ARGS"
fi

# Crie um script para iniciar o serviço - abordagem mais simples e direta
cat > start_service.sh << EOF
#!/bin/bash
cd $PROJECT_DIR
source $PROJECT_DIR/venv/bin/activate
python $PROJECT_DIR/main.py $ARGS
EOF

chmod +x start_service.sh
echo "Script de inicialização criado: $PROJECT_DIR/start_service.sh"

# Script para execução com terminal visível
cat > start_terminal_service.sh << EOF
#!/bin/bash
# Este script inicia o programa em um terminal visível
lxterminal --working-directory=$PROJECT_DIR --command="$PROJECT_DIR/start_service.sh"
EOF

chmod +x start_terminal_service.sh
echo "Script de inicialização com terminal criado: $PROJECT_DIR/start_terminal_service.sh"

# Crie o arquivo de serviço do zero, evitando problemas de substituição
if [ "$TERMINAL_OUTPUT" = true ]; then
    # Versão com terminal visível
    cat > hab_proj_autostart.service << EOF
[Unit]
Description=HAB Project AI Classification System
After=network.target sound.target
After=graphical.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$PROJECT_DIR"
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="DISPLAY=:0"
ExecStart=$PROJECT_DIR/start_terminal_service.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hab-proj

[Install]
WantedBy=graphical.target
EOF
else
    # Versão sem terminal visível (apenas logs)
    cat > hab_proj_autostart.service << EOF
[Unit]
Description=HAB Project AI Classification System
After=network.target sound.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$PROJECT_DIR"
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="DISPLAY=:0"
ExecStart=$PROJECT_DIR/start_service.sh
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hab-proj

[Install]
WantedBy=multi-user.target
EOF
fi

echo "Arquivo de serviço criado com sucesso"

# Copia o arquivo de serviço para o diretório do systemd
echo "Instalando serviço systemd..."
sudo cp hab_proj_autostart.service /etc/systemd/system/

# Recarrega o systemd para reconhecer o novo serviço
sudo systemctl daemon-reload

# Habilita o serviço para iniciar na inicialização
sudo systemctl enable hab_proj_autostart.service

echo "Serviço instalado e habilitado para iniciar na inicialização."
echo "Para iniciar o serviço agora, execute: sudo systemctl start hab_proj_autostart.service"
echo "Para verificar o status, execute: sudo systemctl status hab_proj_autostart.service"
echo "Para parar o serviço, execute: sudo systemctl stop hab_proj_autostart.service"
echo "Para desabilitar a inicialização automática, execute: sudo systemctl disable hab_proj_autostart.service"

# Pergunta se queremos iniciar o serviço agora
read -p "Iniciar o serviço agora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start hab_proj_autostart.service
    sleep 2  # Aguarda um pouco para o serviço iniciar
    echo "Verificando status do serviço:"
    sudo systemctl status hab_proj_autostart.service
    echo "Para ver os logs em tempo real: sudo journalctl -fu hab_proj_autostart.service"
fi

# Criar um script para iniciar manualmente com saída visual (sempre)
cat > run_app.sh << EOF
#!/bin/bash
# Este script inicia a aplicação com saída visível no terminal
cd $PROJECT_DIR
source $PROJECT_DIR/venv/bin/activate
python $PROJECT_DIR/main.py $ARGS
EOF

chmod +x run_app.sh
echo ""
echo "===== IMPORTANTE ====="
echo "Script de execução manual criado: $PROJECT_DIR/run_app.sh"
echo "Você pode executar esse script manualmente a qualquer momento para ver a saída no terminal."
echo "Para usar: ./run_app.sh"
echo "====================" 