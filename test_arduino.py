#!/usr/bin/env python3
"""
Script de teste para enviar comandos para o Arduino.
Este script permite testar a comunicação serial com o Arduino sem precisar
executar todo o sistema de classificação com a câmera.
"""

import argparse
import time
import serial
import serial.tools.list_ports
import threading
import sys
import re

# IDs de produto e fornecedor comuns para placas Arduino
ARDUINO_VID_PID_PATTERNS = [
    # Arduino Uno, Nano, etc.
    r'VID:PID=2341:00[0-9a-fA-F]{2}',  # Arduino oficial
    r'VID:PID=1A86:7523',              # CH340 (clones)
    r'VID:PID=0403:6001',              # FTDI (alguns clones)
    r'VID:PID=0403:6015',              # FTDI (alguns clones)
    r'VID:PID=1A86:55D4',              # CH9102 (alguns clones)
]

def find_arduino_port():
    """
    Tenta encontrar a porta do Arduino automaticamente.
    
    Returns:
        str or None: Porta do Arduino ou None se não encontrada
    """
    # Lista todas as portas seriais disponíveis
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("Nenhuma porta serial encontrada no sistema.")
        return None
        
    print(f"Portas seriais disponíveis: {len(ports)}")
    for port in ports:
        print(f"- {port.device}: {port.description} (hwid: {port.hwid})")
    
    # Estratégia 1: Procurar por portas com descrições ou hwid que contenham "Arduino"
    for port in ports:
        if "arduino" in port.description.lower() or "arduino" in port.hwid.lower():
            print(f"Arduino encontrado na porta {port.device} (descrição/hwid contém 'Arduino')")
            return port.device
    
    # Estratégia 2: Procurar por VID:PID conhecidos de Arduino
    for port in ports:
        for pattern in ARDUINO_VID_PID_PATTERNS:
            if re.search(pattern, port.hwid, re.IGNORECASE):
                print(f"Arduino encontrado na porta {port.device} (VID:PID corresponde a um Arduino)")
                return port.device
    
    # Estratégia 3: Procurar por portas com nomes comuns de Arduino
    arduino_port_patterns = [
        r'(cu|tty)\.usbmodem\d+',  # macOS/Linux Arduino
        r'(cu|tty)\.wchusbserial\d+',  # macOS/Linux CH340
        r'(cu|tty)\.SLAB_USBtoUART',  # macOS/Linux CP210x
        r'COM\d+',  # Windows
    ]
    
    for port in ports:
        for pattern in arduino_port_patterns:
            if re.match(pattern, port.device):
                print(f"Possível Arduino encontrado na porta {port.device} (nome da porta corresponde a um padrão Arduino)")
                return port.device
    
    # Estratégia 4: Se tudo falhar e houver apenas uma porta, use-a
    if len(ports) == 1:
        print(f"Arduino não identificado explicitamente, mas apenas uma porta está disponível: {ports[0].device}")
        return ports[0].device
        
    # Se chegamos aqui, não conseguimos identificar o Arduino
    print("Não foi possível identificar uma porta Arduino. Portas disponíveis:")
    for port in ports:
        print(f"- {port.device}: {port.description} (hwid: {port.hwid})")
    
    return None

def serial_reader(ser, stop_event):
    """
    Função para ler continuamente da porta serial em uma thread separada.
    
    Args:
        ser (serial.Serial): Objeto de conexão serial
        stop_event (threading.Event): Evento para sinalizar quando parar a thread
    """
    print("Iniciando leitura da porta serial. Pressione Ctrl+C para sair.")
    try:
        while not stop_event.is_set():
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Arduino: {line}")
            time.sleep(0.1)  # Pequena pausa para não sobrecarregar a CPU
    except Exception as e:
        print(f"Erro na thread de leitura: {e}")

def verify_arduino_connection(ser):
    """
    Verifica se o Arduino está realmente conectado e respondendo.
    
    Args:
        ser (serial.Serial): Objeto de conexão serial
        
    Returns:
        bool: True se o Arduino está respondendo, False caso contrário
    """
    # Limpar o buffer de entrada
    ser.reset_input_buffer()
    
    # Enviar um comando de ping
    print("Verificando conexão com o Arduino...")
    
    # Enviar múltiplos pings para aumentar a chance de resposta
    for attempt in range(3):
        print(f"Tentativa {attempt+1}/3...")
        ser.write(b"ping\n")
        ser.flush()
        
        # Aguardar resposta
        start_time = time.time()
        while time.time() - start_time < 1:  # Timeout de 1 segundo por tentativa
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if "Arduino pronto" in response:
                    print("Arduino conectado e respondendo!")
                    return True
                else:
                    print(f"Resposta recebida: {response}")
            time.sleep(0.1)
    
    print("AVISO: Arduino não respondeu ao ping. A porta serial está aberta, mas o Arduino pode não estar conectado ou não estar executando o código correto.")
    return False

def send_command(port, command, baudrate=9600, monitor_mode=False):
    """
    Envia um comando para o Arduino e opcionalmente monitora a porta serial.
    
    Args:
        port (str): Porta serial do Arduino
        command (int): Comando a ser enviado (0 ou 1)
        baudrate (int): Taxa de transmissão (baud rate)
        monitor_mode (bool): Se deve entrar no modo de monitoramento contínuo
    """
    try:
        # Conectar à porta serial
        print(f"Tentando conectar à porta {port}...")
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"Porta serial {port} aberta com baudrate {baudrate}")
        
        # Aguardar a inicialização do Arduino
        time.sleep(2)
        
        # Verificar se o Arduino está realmente conectado e respondendo
        arduino_connected = verify_arduino_connection(ser)
        
        # Se o Arduino não está respondendo e estamos no modo de monitoramento, não continue
        if not arduino_connected and monitor_mode:
            print("Erro: Não é possível entrar no modo de monitoramento sem um Arduino conectado.")
            ser.close()
            return
        
        # Se o Arduino não está respondendo mas não estamos no modo de monitoramento, avise mas continue
        if not arduino_connected and not monitor_mode:
            print("Continuando mesmo sem confirmação do Arduino...")
        
        # Enviar o comando
        cmd_str = str(command) + '\n'
        print(f"Enviando comando: {command}")
        ser.write(cmd_str.encode())
        
        # Se não estiver no modo de monitoramento, apenas lê a resposta imediata
        if not monitor_mode:
            # Aguardar e ler a resposta
            time.sleep(0.5)
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Resposta do Arduino: {response}")
            else:
                print("Nenhuma resposta recebida do Arduino.")
            
            # Fechar a conexão
            ser.close()
            print("Conexão fechada")
        else:
            # Entrar no modo de monitoramento contínuo
            stop_event = threading.Event()
            reader_thread = threading.Thread(target=serial_reader, args=(ser, stop_event))
            reader_thread.daemon = True
            reader_thread.start()
            
            print("Modo de monitoramento ativado. Pressione Ctrl+C para sair.")
            print("Você pode enviar comandos adicionais digitando '0' ou '1' seguido de Enter:")
            
            try:
                while True:
                    # Ler entrada do usuário
                    user_input = input()
                    if user_input.strip() in ['0', '1']:
                        cmd = user_input.strip() + '\n'
                        ser.write(cmd.encode())
                        print(f"Comando enviado: {user_input.strip()}")
                    elif user_input.lower() == 'exit' or user_input.lower() == 'quit':
                        break
                    else:
                        print("Comando inválido. Use '0' ou '1', ou 'exit' para sair.")
            except KeyboardInterrupt:
                print("\nInterrompido pelo usuário.")
            finally:
                # Parar a thread de leitura e fechar a conexão
                stop_event.set()
                reader_thread.join(timeout=1.0)
                ser.close()
                print("Conexão fechada")
        
    except serial.SerialException as e:
        print(f"Erro ao conectar ou enviar comando: {e}")
        print("Verifique se o Arduino está conectado e se a porta está correta.")
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Conexão fechada")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Teste de comunicação com Arduino')
    
    # Cria um grupo de argumentos mutuamente exclusivos
    group = parser.add_mutually_exclusive_group(required=True)
    
    # Adiciona o comando como um argumento opcional dentro do grupo
    group.add_argument('--command', type=int, choices=[0, 1],
                      help='Comando a ser enviado (0: Desligar LED, 1: Ligar LED)')
    
    # Adiciona a opção --list-ports ao grupo mutuamente exclusivo
    group.add_argument('--list-ports', action='store_true',
                      help='Listar todas as portas seriais disponíveis e sair')
    
    parser.add_argument('--port', type=str, default=None,
                        help='Porta serial do Arduino (ex: /dev/ttyUSB0, COM3). Se não especificada, tentará detectar automaticamente.')
    
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Taxa de transmissão (baud rate) para comunicação serial (padrão: 9600)')
    
    parser.add_argument('--monitor', action='store_true',
                        help='Ativar modo de monitoramento contínuo da porta serial')
    
    args = parser.parse_args()
    
    # Se a opção --list-ports foi especificada, apenas lista as portas e sai
    if args.list_ports:
        find_arduino_port()
        return
    
    # Se a porta não foi especificada, tenta encontrar automaticamente
    if args.port is None:
        args.port = find_arduino_port()
        if args.port is None:
            print("Erro: Não foi possível encontrar o Arduino. Verifique a conexão ou especifique a porta manualmente.")
            return
    
    # Enviar o comando e opcionalmente monitorar a porta serial
    send_command(args.port, args.command, args.baudrate, args.monitor)

if __name__ == "__main__":
    main() 