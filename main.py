#!/usr/bin/env python3
"""
HAB Project - Sistema de Classificação com IA
Aplicação principal que integra câmera e modelo de IA.
"""

import os
import argparse
from hab_proj.model import AIModel
from hab_proj.camera import Camera
from hab_proj.serial_comm import ArduinoSerial

def parse_args():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos analisados
    """
    parser = argparse.ArgumentParser(description='HAB Project - Sistema de Classificação com IA')
    
    parser.add_argument('--camera', type=int, default=0,
                        help='ID da câmera (padrão: 0, geralmente a webcam integrada)')
    
    parser.add_argument('--model', type=str, default='converted_keras/keras_model.h5',
                        help='Caminho para o arquivo do modelo (padrão: converted_keras/keras_model.h5)')
    
    parser.add_argument('--labels', type=str, default='converted_keras/labels.txt',
                        help='Caminho para o arquivo de labels (padrão: converted_keras/labels.txt)')
    
    parser.add_argument('--interval', type=float, default=0.5,
                        help='Intervalo em segundos entre predições (padrão: 0.5)')
    
    parser.add_argument('--no-fps', action='store_true',
                        help='Não exibir FPS na tela')
    
    # Argumentos para comunicação serial com Arduino
    parser.add_argument('--arduino', action='store_true',
                        help='Habilitar comunicação com Arduino')
    
    parser.add_argument('--port', type=str, default=None,
                        help='Porta serial do Arduino (ex: /dev/ttyUSB0, COM3). Se não especificada, tentará detectar automaticamente.')
    
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Taxa de transmissão (baud rate) para comunicação serial (padrão: 9600)')
    
    parser.add_argument('--allow-no-arduino', action='store_true',
                        help='Permitir execução mesmo se o Arduino não estiver respondendo')
    
    return parser.parse_args()

def main():
    """Função principal da aplicação."""
    # Analisar argumentos
    args = parse_args()
    
    # Verificar se os arquivos do modelo existem
    if not os.path.exists(args.model):
        print(f"Erro: Arquivo do modelo não encontrado: {args.model}")
        return
    
    if not os.path.exists(args.labels):
        print(f"Erro: Arquivo de labels não encontrado: {args.labels}")
        return
    
    try:
        # Carregar o modelo de IA
        print(f"Carregando modelo de IA de {args.model}...")
        model = AIModel(args.model, args.labels)
        print("Modelo carregado com sucesso!")
        
        # Inicializar a comunicação serial com Arduino se solicitado
        arduino_serial = None
        if args.arduino:
            print("Inicializando comunicação com Arduino...")
            arduino_serial = ArduinoSerial(
                port=args.port,
                baudrate=args.baudrate,
                require_arduino=not args.allow_no_arduino
            )
            
            # Tentar conectar ao Arduino
            if arduino_serial.connect():
                if arduino_serial.arduino_responding:
                    print(f"Arduino conectado e respondendo na porta {arduino_serial.port}")
                else:
                    if args.allow_no_arduino:
                        print("Aviso: Arduino não está respondendo, mas continuando mesmo assim porque --allow-no-arduino foi especificado.")
                    else:
                        print("Erro: Arduino não está respondendo. Use --allow-no-arduino para continuar mesmo assim.")
                        return
            else:
                print("Erro: Não foi possível conectar ao Arduino.")
                return
        
        # Inicializar a câmera com o modelo e Arduino
        camera = Camera(
            camera_id=args.camera, 
            model=model,
            arduino_serial=arduino_serial
        )
        
        # Executar a câmera com o modelo
        print(f"Iniciando câmera {args.camera} com classificação em tempo real...")
        if arduino_serial and arduino_serial.arduino_responding:
            print("Comunicação com Arduino ativada. Enviando comandos baseados nas predições:")
            print("  - 'Bom' -> Envia '1'")
            print("  - 'Ruim' -> Envia '0'")
            print("  - 'Nada' -> Não envia nada")
        
        print("Pressione 'q' para sair.")
        
        camera.run_with_model(
            display_fps=not args.no_fps,
            prediction_interval=args.interval
        )
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main() 