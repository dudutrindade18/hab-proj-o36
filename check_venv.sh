#!/bin/bash

# Script para verificar e garantir que as dependências estão instaladas no ambiente virtual

echo "===== Verificando ambiente virtual e dependências ====="

# Obter o diretório atual do projeto
PROJECT_DIR=$(pwd)
echo "Diretório do projeto: $PROJECT_DIR"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
fi

# Ativar o ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se está usando o Python do ambiente virtual
VENV_PYTHON=$(which python)
echo "Usando Python: $VENV_PYTHON"

# Instalar ou atualizar dependências
echo "Atualizando pip..."
python -m pip install --upgrade pip

echo "Instalando dependências..."
python -m pip install -r requirements.txt

# Verificar especificamente o NumPy
echo "Verificando instalação do NumPy..."
python -c "import numpy; print('NumPy versão:', numpy.__version__)"

# Verificar outras dependências importantes
echo "Verificando outras dependências..."
python -c "import cv2; print('OpenCV versão:', cv2.__version__)"
python -c "import tensorflow; print('TensorFlow versão:', tensorflow.__version__)"
python -c "import PIL; print('PIL versão:', PIL.__version__)"
python -c "import serial; print('PySerial versão:', serial.__version__)"

echo "===== Verificação concluída ====="
echo "O ambiente virtual está configurado corretamente."
echo "Para testar o programa manualmente, execute:"
echo "source venv/bin/activate && python main.py"

# Perguntar se deseja modificar o serviço systemd
read -p "Deseja reinstalar o serviço de autostart? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Atualizar o serviço systemd
    CURRENT_USER=$(whoami)
    
    # Backup do arquivo original
    cp hab_proj_autostart.service hab_proj_autostart.service.bak
    
    # Atualizar o usuário e caminhos
    sed -i "s|User=hab-proj5|User=$CURRENT_USER|g" hab_proj_autostart.service
    sed -i "s|/home/hab-proj5/Desktop/hab-proj-o36|$PROJECT_DIR|g" hab_proj_autostart.service
    
    # Instalar o serviço
    echo "Instalando o serviço..."
    sudo cp hab_proj_autostart.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable hab_proj_autostart.service
    
    echo "Serviço instalado. Para iniciar:"
    echo "sudo systemctl start hab_proj_autostart.service"
fi 