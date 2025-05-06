#!/bin/bash

# HAB Project - Autostart Setup Script
# This script sets up the HAB Project to start automatically on boot

echo "===== HAB Project - Autostart Setup ====="

# Get the current username
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

# Update the service file with the correct username and paths
sed -i "s|User=hab-proj5|User=$CURRENT_USER|g" hab_proj_autostart.service
sed -i "s|/home/hab-proj5/Desktop/hab-proj-o36|$PROJECT_DIR|g" hab_proj_autostart.service

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

# Defina todos os argumentos
ARGS="$ARDUINO_FLAG $VOICE_FLAG $HEADLESS_FLAG"

# Adicione quaisquer argumentos de linha de comando adicionais
read -p "Adicione quaisquer argumentos adicionais de linha de comando (exemplo: --low-power): " EXTRA_ARGS
if [ ! -z "$EXTRA_ARGS" ]; then
    ARGS="$ARGS $EXTRA_ARGS"
fi

# Atualize o comando ExecStart no arquivo de serviço
sed -i "s|python /.*main.py.*|python $PROJECT_DIR/main.py $ARGS'|g" hab_proj_autostart.service

# Crie um script para iniciar o serviço
cat > start_service.sh << EOF
#!/bin/bash
source $PROJECT_DIR/venv/bin/activate
cd $PROJECT_DIR
python main.py $ARGS
EOF

chmod +x start_service.sh

# Update ExecStart to use the script
sed -i "s|ExecStart=.*|ExecStart=/bin/bash -c '$PROJECT_DIR/start_service.sh'|g" hab_proj_autostart.service

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
    echo "Serviço iniciado. Verifique o status com: sudo systemctl status hab_proj_autostart.service"
    echo "Para ver os logs em tempo real: sudo journalctl -fu hab_proj_autostart.service"
fi 