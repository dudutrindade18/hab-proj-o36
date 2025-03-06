#!/usr/bin/env python3
"""
HAB Project - Sistema de Classificação com IA
Aplicação principal que integra câmera e modelo de IA.
"""

import os
import argparse
from hab_proj.model import AIModel
from hab_proj.camera import Camera

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
        
        # Inicializar a câmera com o modelo
        camera = Camera(camera_id=args.camera, model=model)
        
        # Executar a câmera com o modelo
        print(f"Iniciando câmera {args.camera} com classificação em tempo real...")
        print("Pressione 'q' para sair.")
        camera.run_with_model(
            display_fps=not args.no_fps,
            prediction_interval=args.interval
        )
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main() 