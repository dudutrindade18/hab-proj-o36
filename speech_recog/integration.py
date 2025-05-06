import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from speech_recog.voice_control import VoiceControl

def setup_voice_recognition(on_command_callback=None):
    """
    Configura e inicia o reconhecimento de voz
    
    Args:
        on_command_callback: Função a ser chamada quando um comando for reconhecido
                            Formato: callback(command, value)
                            Onde command é a string e value é o valor associado (0-100)
    
    Returns:
        VoiceControl: Instância do controlador de voz
    """
    # Verifica se o modelo está disponível, caso contrário, baixa
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model-en-us-small")
    
    if not os.path.exists(model_path):
        print("Modelo de voz não encontrado. Baixando...")
        from speech_recog.download_model import download_model
        download_model()
    
    # Cria e inicia o controle de voz
    voice_control = VoiceControl(callback=on_command_callback)
    voice_control.start()
    
    return voice_control

def setup_default_voice_commands(arduino_serial=None):
    """
    Configuração padrão para reconhecimento de voz que envia comandos para o Arduino
    
    Args:
        arduino_serial: Instância do objeto de comunicação serial com o Arduino
    
    Returns:
        VoiceControl: Instância do controlador de voz
    """
    def on_voice_command(command, value):
        """Função chamada quando um comando de voz é reconhecido"""
        # Se não houver comunicação com o Arduino, apenas exibe na tela
        if not arduino_serial:
            print(f"[VOICE] Comando: {command}, Valor: {value}")
            return
            
        # Mapeia comandos para sinais do Arduino
        if command == "low":
            arduino_serial.send_command('2')  # Valor baixo
            print(f"[VOICE] Enviando comando LOW ({value}) para o Arduino")
            
        elif command == "medium":
            arduino_serial.send_command('3')  # Valor médio
            print(f"[VOICE] Enviando comando MEDIUM ({value}) para o Arduino")
            
        elif command == "maximum":
            arduino_serial.send_command('4')  # Valor máximo
            print(f"[VOICE] Enviando comando MAXIMUM ({value}) para o Arduino")
    
    # Configura e inicia o reconhecimento de voz com a função de callback
    return setup_voice_recognition(on_command_callback=on_voice_command)

# Exemplo de uso direto
if __name__ == "__main__":
    # Testa a integração sem Arduino
    voice_control = setup_default_voice_commands()
    
    try:
        import time
        print("Sistema de reconhecimento de voz ativo.")
        print("Diga 'low', 'medium' ou 'maximum' para testar.")
        print("Pressione Ctrl+C para encerrar.")
        
        # Mantém o programa em execução
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
    finally:
        # Para o reconhecimento de voz
        if voice_control:
            voice_control.stop() 