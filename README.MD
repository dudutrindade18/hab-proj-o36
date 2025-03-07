# HAB Project - Sistema de Classificação com IA

Esse projeto integra uma câmera com um modelo de IA para classificação em tempo real. O sistema captura imagens da webcam, processa-as usando um modelo de IA treinado e exibe os resultados na tela. Também suporta comunicação serial com Arduino para enviar comandos baseados nas classificações.

## Estrutura do Projeto

```
hab-proj-o36/
├── arduino_code/          # Pasta com o código para o Arduino
│   └── hab_proj_receiver.ino  # Código do Arduino para receber comandos
├── converted_keras/       # Pasta com o modelo de IA
│   ├── keras_model.h5     # Arquivo do modelo Keras
│   └── labels.txt         # Arquivo com as labels do modelo
├── hab_proj/              # Pacote principal do projeto
│   ├── __init__.py        # Arquivo de inicialização do pacote
│   ├── camera.py          # Módulo para gerenciar a câmera
│   ├── model.py           # Módulo para gerenciar o modelo de IA
│   └── serial_comm.py     # Módulo para comunicação serial com Arduino
├── main.py                # Ponto de entrada da aplicação
├── requirements.txt       # Dependências do projeto
├── setup.sh               # Script de configuração
└── webcam.py              # Script original da webcam (mantido para referência)
```

## Requisitos

- Python 3.9
- OpenCV
- TensorFlow
- NumPy
- Pillow
- PySerial (para comunicação com Arduino)

## Instalação

1. Clone o repositório:
   ```
   git clone <https://github.com/dudutrindade18/hab-proj-o36>
   cd hab-proj-o36
   ```

2. Execute o script de configuração:
   ```
   ./setup.sh
   ```
   Este script irá:
   - Criar um ambiente virtual Python
   - Ativar o ambiente virtual
   - Instalar todas as dependências necessárias
   - Tornar o arquivo main.py executável

3. Ative o ambiente virtual:
   ```
   source venv/bin/activate
   ```

## Uso

Execute o programa principal:

```
python main.py
```

### Opções de Linha de Comando

#### Opções Gerais
- `--camera`: ID da câmera (padrão: 0, geralmente a webcam integrada)
- `--model`: Caminho para o arquivo do modelo (padrão: converted_keras/keras_model.h5)
- `--labels`: Caminho para o arquivo de labels (padrão: converted_keras/labels.txt)
- `--interval`: Intervalo em segundos entre predições (padrão: 0.5)
- `--no-fps`: Não exibir FPS na tela

#### Opções para Arduino
- `--arduino`: Habilitar comunicação com Arduino
- `--port`: Porta serial do Arduino (ex: /dev/ttyUSB0, COM3). Se não especificada, tentará detectar automaticamente.
- `--baudrate`: Taxa de transmissão (baud rate) para comunicação serial (padrão: 9600)

### Exemplos

Executar com a webcam padrão:
```
python main.py
```

Executar com comunicação Arduino:
```
python main.py --arduino
```

Especificar porta do Arduino:
```
python main.py --arduino --port /dev/ttyUSB0
```

Usar câmera externa e intervalo de predição mais rápido:
```
python main.py --camera 1 --interval 0.2 --arduino
```

## Funcionamento

1. O programa carrega o modelo de IA especificado.
2. Se a opção `--arduino` for fornecida, tenta conectar ao Arduino.
3. Inicializa a câmera e começa a capturar frames.
4. Em intervalos regulares, o frame atual é processado pelo modelo de IA.
5. O resultado da classificação é exibido na tela junto com a confiança da predição.
6. Se conectado ao Arduino, envia comandos baseados na classificação:
   - "Bom" -> Envia "1"
   - "Ruim" -> Envia "0"
   - "Nada" -> Não envia nada
7. Pressione 'q' para sair do programa.

## Comunicação com Arduino

O sistema envia comandos para o Arduino baseados nas classificações do modelo:

- Quando a classificação é "Bom", envia o valor "1"
- Quando a classificação é "Ruim", envia o valor "0"
- Quando a classificação é "Nada", não envia nenhum comando

### Configuração do Arduino

Para que o Arduino receba corretamente os comandos:

1. Abra o arquivo `arduino_code/hab_proj_receiver.ino` no Arduino IDE
2. Faça upload do código para o seu Arduino
3. Conecte o Arduino ao computador via USB
4. Execute a aplicação Python com a opção `--arduino`

O código do Arduino está configurado para:
- Inicializar a comunicação serial com taxa de 9600 baud
- Piscar o LED 3 vezes na inicialização para indicar que está pronto
- Ligar o LED embutido quando receber o comando "1" (classificação "Bom")
- Desligar o LED embutido quando receber o comando "0" (classificação "Ruim")
- Enviar confirmação via serial após cada ação

## Classes do Modelo

O modelo atual classifica as imagens em três categorias:
- 0: Bom
- 1: Ruim
- 2: Nada

## Desenvolvimento

### Módulos Principais

#### hab_proj.model.AIModel

Classe responsável por carregar e utilizar o modelo de IA para classificação.

Métodos principais:
- `__init__(model_path, labels_path)`: Inicializa o modelo
- `predict(image)`: Realiza a predição em uma imagem

#### hab_proj.camera.Camera

Classe para gerenciar a câmera e integrar com o modelo de IA.

Métodos principais:
- `__init__(camera_id, model, arduino_serial)`: Inicializa a câmera
- `start()`: Inicia a câmera
- `stop()`: Libera os recursos da câmera
- `run_with_model(display_fps, prediction_interval)`: Executa a câmera com o modelo de IA

#### hab_proj.serial_comm.ArduinoSerial

Classe para gerenciar a comunicação serial com o Arduino.

Métodos principais:
- `__init__(port, baudrate, timeout)`: Inicializa a comunicação serial
- `connect()`: Conecta ao Arduino
- `disconnect()`: Desconecta do Arduino
- `send_command(command)`: Envia um comando para o Arduino
- `send_label_command(label)`: Envia um comando baseado na label do modelo