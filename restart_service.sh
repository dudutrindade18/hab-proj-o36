#!/bin/bash

# Script para reiniciar e verificar o serviço HAB

echo "===== HAB Project Service Manager ====="

# Verificar se está rodando como root/sudo
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute este script com sudo"
  exit 1
fi

# Parar o serviço
echo "Parando o serviço..."
systemctl stop hab_proj_autostart.service

# Recarregar as configurações do systemd
echo "Recarregando configurações do systemd..."
systemctl daemon-reload

# Iniciar o serviço
echo "Iniciando o serviço..."
systemctl start hab_proj_autostart.service

# Verificar status
echo "Status do serviço:"
systemctl status hab_proj_autostart.service

# Mostrar opções para ver logs
echo ""
echo "Para ver os logs completos, execute:"
echo "sudo journalctl -u hab_proj_autostart.service"
echo ""
echo "Para ver os logs em tempo real, execute:"
echo "sudo journalctl -u hab_proj_autostart.service -f" 