"""
Módulo para gerenciar a comunicação serial com o Arduino.
"""

import serial
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArduinoSerial:
    """Classe para gerenciar a comunicação serial com o Arduino."""
    
    def __init__(self, port=None, baudrate=9600, timeout=1, require_arduino=True):
        """
        Inicializa a comunicação serial com o Arduino.
        
        Args:
            port (str, optional): Porta serial (ex: '/dev/ttyUSB0', 'COM3'). 
                                 Se None, tentará encontrar automaticamente.
            baudrate (int): Taxa de transmissão (baud rate)
            timeout (float): Tempo limite para operações de leitura em segundos
            require_arduino (bool): Se True, exige que o Arduino esteja realmente conectado e respondendo
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False
        self.arduino_responding = False
        self.require_arduino = require_arduino
        
    def connect(self):
        """
        Conecta ao Arduino.
        
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário
        """
        if self.is_connected:
            return True
            
        try:
            # Se a porta não foi especificada, tenta encontrar automaticamente
            if self.port is None:
                self.port = self._find_arduino_port()
                if self.port is None:
                    logger.error("Não foi possível encontrar o Arduino. Verifique a conexão.")
                    return False
            
            # Conecta à porta serial
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Aguarda a inicialização do Arduino (importante para placas que resetam ao conectar)
            time.sleep(2)
            
            # Verifica se o Arduino está realmente respondendo
            self.arduino_responding = self._verify_arduino_connection()
            
            # Se o Arduino não está respondendo e é obrigatório, falha na conexão
            if not self.arduino_responding and self.require_arduino:
                logger.error("Arduino não está respondendo. Verifique a conexão física e o código no Arduino.")
                self.serial_conn.close()
                return False
            
            self.is_connected = True
            if self.arduino_responding:
                logger.info(f"Conectado ao Arduino na porta {self.port} e Arduino está respondendo")
            else:
                logger.warning(f"Porta serial {self.port} aberta, mas o Arduino não está respondendo. Verifique a conexão física e o código no Arduino.")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Erro ao conectar ao Arduino: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do Arduino."""
        if self.serial_conn and self.is_connected:
            self.serial_conn.close()
            self.is_connected = False
            self.arduino_responding = False
            logger.info("Desconectado do Arduino")
    
    def _verify_arduino_connection(self):
        """
        Verifica se o Arduino está realmente conectado e respondendo.
        
        Returns:
            bool: True se o Arduino está respondendo, False caso contrário
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
            
        # Limpar o buffer de entrada
        self.serial_conn.reset_input_buffer()
        
        # Enviar um comando de ping
        logger.info("Verificando conexão com o Arduino...")
        try:
            self.serial_conn.write(b"ping\n")
            self.serial_conn.flush()
            
            # Aguardar resposta
            start_time = time.time()
            while time.time() - start_time < 3:  # Timeout de 3 segundos
                if self.serial_conn.in_waiting:
                    response = self.serial_conn.readline().decode('utf-8').strip()
                    if "Arduino pronto" in response:
                        logger.info("Arduino conectado e respondendo!")
                        return True
                    else:
                        logger.info(f"Resposta recebida: {response}")
                time.sleep(0.1)
            
            logger.warning("Arduino não respondeu ao ping. A porta serial está aberta, mas o Arduino pode não estar conectado ou não estar executando o código correto.")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com Arduino: {e}")
            return False
    
    def send_command(self, command):
        """
        Envia um comando para o Arduino.
        
        Args:
            command: Comando a ser enviado (será convertido para string e terminado com newline)
            
        Returns:
            bool: True se o comando foi enviado com sucesso, False caso contrário
        """
        if not self.is_connected:
            if not self.connect():
                return False
        
        # Se o Arduino não está respondendo e é obrigatório, não envia o comando
        if not self.arduino_responding and self.require_arduino:
            logger.error("Não é possível enviar comando: Arduino não está respondendo")
            return False
        
        try:
            # Converte o comando para string e adiciona newline
            cmd_str = str(command) + '\n'
            # Envia o comando como bytes
            self.serial_conn.write(cmd_str.encode())
            self.serial_conn.flush()
            logger.debug(f"Comando enviado: {command}")
            
            # Se o Arduino está respondendo, aguarda e lê a resposta
            if self.arduino_responding:
                time.sleep(0.5)
                if self.serial_conn.in_waiting:
                    response = self.serial_conn.readline().decode('utf-8').strip()
                    logger.debug(f"Resposta do Arduino: {response}")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Erro ao enviar comando: {e}")
            self.is_connected = False
            return False
    
    def send_label_command(self, label):
        """
        Envia um comando baseado na label do modelo.
        
        Args:
            label (str): Label do modelo ('Bom', 'Ruim', 'Nada')
            
        Returns:
            bool: True se o comando foi enviado com sucesso, False caso contrário
        """
        if label == "Bom":
            logger.info("Label 'Bom' detectada. Enviando comando '1'")
            return self.send_command(1)
        elif label == "Ruim":
            logger.info("Label 'Ruim' detectada. Enviando comando '0'")
            return self.send_command(0)
        elif label == "Nada":
            logger.debug("Label 'Nada' detectada. Nenhum comando enviado.")
            return True
        else:
            logger.warning(f"Label desconhecida: {label}. Nenhum comando enviado.")
            return False
    
    def _find_arduino_port(self):
        """
        Tenta encontrar a porta do Arduino automaticamente.
        
        Returns:
            str or None: Porta do Arduino ou None se não encontrada
        """
        import serial.tools.list_ports
        
        # Lista todas as portas seriais disponíveis
        ports = list(serial.tools.list_ports.comports())
        
        # Procura por portas que possam ser um Arduino
        for port in ports:
            # Arduino geralmente tem "Arduino" ou "CH340" ou "FTDI" na descrição
            if "Arduino" in port.description or "CH340" in port.description or "FTDI" in port.description:
                logger.info(f"Arduino encontrado na porta {port.device}")
                return port.device
                
        # Se não encontrou nenhuma porta com descrição de Arduino, tenta a primeira disponível
        if ports:
            logger.warning(f"Arduino não identificado explicitamente. Usando a primeira porta disponível: {ports[0].device}")
            return ports[0].device
            
        return None 