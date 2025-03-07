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
├── test_arduino.py        # Script para testar a comunicação com o Arduino
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

Por padrão, o programa tentará se conectar ao Arduino. Se você não tiver um Arduino conectado, use a opção `--no-arduino`.

### Opções de Linha de Comando

#### Opções Gerais
- `--camera`: ID da câmera (padrão: 0, geralmente a webcam integrada)
- `--model`: Caminho para o arquivo do modelo (padrão: converted_keras/keras_model.h5)
- `--labels`: Caminho para o arquivo de labels (padrão: converted_keras/labels.txt)
- `--interval`: Intervalo em segundos entre predições (padrão: 0.5)
- `--no-fps`: Não exibir FPS na tela

#### Opções para Arduino
- `--no-arduino`: Desabilitar comunicação com Arduino (por padrão, a comunicação está habilitada)
- `--port`: Porta serial do Arduino (ex: /dev/ttyUSB0, COM3). Se não especificada, tentará detectar automaticamente.
- `--baudrate`: Taxa de transmissão (baud rate) para comunicação serial (padrão: 9600)
- `--allow-no-arduino`: Permitir execução mesmo se o Arduino não estiver respondendo

### Exemplos

Executar com a webcam padrão (com Arduino, se disponível):
```
python main.py
```

Executar sem Arduino:
```
python main.py --no-arduino
```

Especificar porta do Arduino:
```
python main.py --port /dev/ttyUSB0
```

Usar câmera externa e intervalo de predição mais rápido:
```
python main.py --camera 1 --interval 0.2
```

Permitir execução mesmo sem Arduino respondendo:
```
python main.py --allow-no-arduino
```

## Testando a Comunicação com o Arduino

Para testar a comunicação com o Arduino sem executar todo o sistema de classificação, use o script `test_arduino.py`:

### Listar Portas Disponíveis

Para listar todas as portas seriais disponíveis e identificar o Arduino:

```
python test_arduino.py --list-ports
```

### Enviar Comandos

Para enviar comandos para o Arduino:

```
python test_arduino.py --command [0|1] [opções]
```

#### Opções

- `--port`: Porta serial do Arduino (ex: /dev/ttyUSB0, COM3). Se não especificada, tentará detectar automaticamente.
- `--baudrate`: Taxa de transmissão (baud rate) para comunicação serial (padrão: 9600)
- `--monitor`: Ativar modo de monitoramento contínuo da porta serial

#### Exemplos

Ligar o LED (enviar comando 1):
```
python test_arduino.py --command 1
```

Desligar o LED (enviar comando 0):
```
python test_arduino.py --command 0
```

Especificar a porta manualmente:
```
python test_arduino.py --command 1 --port /dev/ttyUSB0
```

Monitorar a porta serial continuamente:
```
python test_arduino.py --command 1 --monitor
```

### Modo de Monitoramento

Quando você usa a opção `--monitor`, o script entra em um modo interativo que:

1. Envia o comando inicial especificado
2. Monitora continuamente todas as mensagens enviadas pelo Arduino
3. Permite enviar comandos adicionais digitando '0' ou '1' seguido de Enter
4. Continua até que você pressione Ctrl+C ou digite 'exit'

Este modo é útil para:
- Depurar a comunicação com o Arduino
- Testar diferentes comandos em sequência
- Monitorar as respostas do Arduino em tempo real

**Nota**: O modo de monitoramento só funciona se um Arduino real estiver conectado e respondendo. O script verificará isso antes de entrar no modo de monitoramento.

## Verificação de Conexão do Arduino

O sistema agora verifica se o Arduino está realmente conectado e respondendo, não apenas se a porta serial pode ser aberta. Isso é feito enviando um comando "ping" e esperando uma resposta específica.

Se o Arduino não estiver respondendo:
- O script de teste não entrará no modo de monitoramento
- O programa principal não iniciará, a menos que você use a opção `--allow-no-arduino`

Isso evita situações em que o programa parece estar funcionando, mas na verdade não há um Arduino conectado ou o Arduino não está executando o código correto.

## Detecção Automática de Portas

O sistema usa várias estratégias para detectar automaticamente a porta do Arduino:

1. Procura por portas com "Arduino" na descrição ou no hardware ID
2. Procura por VID:PID (identificadores de produto e fornecedor) conhecidos de Arduino
3. Procura por nomes de portas que seguem padrões comuns de Arduino
4. Se houver apenas uma porta disponível, usa-a como último recurso

Isso torna o sistema mais robusto em diferentes sistemas operacionais e com diferentes tipos de placas Arduino.

## Funcionamento

1. O programa carrega o modelo de IA especificado.
2. Por padrão, tenta conectar ao Arduino e verifica se ele está respondendo (a menos que `--no-arduino` seja especificado).
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
4. Execute a aplicação Python (main.py).

O código do Arduino está configurado para:
- Inicializar a comunicação serial com taxa de 9600 baud
- Piscar o LED 3 vezes na inicialização para indicar que está pronto
- Responder a comandos "ping" para verificação de conexão
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
- `__init__(port, baudrate, timeout, require_arduino)`: Inicializa a comunicação serial
- `connect()`: Conecta ao Arduino e verifica se ele está respondendo
- `disconnect()`: Desconecta do Arduino
- `send_command(command)`: Envia um comando para o Arduino
- `send_label_command(label)`: Envia um comando baseado na label do modelo
