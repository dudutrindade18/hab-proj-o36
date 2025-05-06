#!/bin/bash

# HAB Project - Autostart Setup Script (Simplified)
# Este script configura o HAB Project para iniciar automaticamente no boot

echo "===== HAB Project - Autostart Setup ====="

# Obter usuário atual e diretório
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

# Configurar grupos para o usuário (necessário para áudio e serial)
echo "Configurando permissões para áudio e serial..."
sudo usermod -a -G audio $CURRENT_USER
sudo usermod -a -G dialout $CURRENT_USER
echo "Adicionado aos grupos necessários. Efetivo após reiniciar."

# Criar o arquivo de serviço com configurações fixas
echo "Criando arquivo de serviço..."
cat > hab_proj_autostart.service << EOF
[Unit]
Description=HAB Project AI Classification System
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$PROJECT_DIR"
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="DISPLAY=:0"
ExecStart=/usr/bin/lxterminal --working-directory=$PROJECT_DIR --command="$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py --headless"
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hab-proj

[Install]
WantedBy=multi-user.target
EOF

# Instalar o serviço
echo "Instalando serviço..."
sudo cp hab_proj_autostart.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hab_proj_autostart.service

# Corrigir permissões
echo "Corrigindo permissões..."
sudo chown -R $CURRENT_USER:$CURRENT_USER $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "===== Configuração Concluída! ====="
echo "O programa HAB Project foi configurado para iniciar automaticamente no boot."
echo "Configurações usadas: headless (sem interface), com Arduino, com reconhecimento de voz"
echo ""
echo "Para iniciar agora: sudo systemctl start hab_proj_autostart.service"
echo "Para verificar status: sudo systemctl status hab_proj_autostart.service"
echo ""
echo "Para que as permissões sejam aplicadas, é necessário reiniciar o sistema."
echo "Deseja reiniciar agora? (s/n)"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sudo reboot
fi 