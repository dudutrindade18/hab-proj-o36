# HAB Project - Sistema de Classificação com IA

Esse projeto integra uma câmera com um modelo de IA para classificação em tempo real. O sistema captura imagens da webcam, processa-as usando um modelo de IA treinado e exibe os resultados na tela.

## Estrutura do Projeto

```
hab-proj-o36/
├── converted_keras/       # Pasta com o modelo de IA
│   ├── keras_model.h5     # Arquivo do modelo Keras
│   └── labels.txt         # Arquivo com as labels do modelo
├── hab_proj/              # Pacote principal do projeto
│   ├── __init__.py        # Arquivo de inicialização do pacote
│   ├── camera.py          # Módulo para gerenciar a câmera
│   └── model.py           # Módulo para gerenciar o modelo de IA
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

## Uso

Execute o programa principal:

```
python main.py
```

### Opções de Linha de Comando

- `--camera`: ID da câmera (padrão: 0, geralmente a webcam integrada)
- `--model`: Caminho para o arquivo do modelo (padrão: converted_keras/keras_model.h5)
- `--labels`: Caminho para o arquivo de labels (padrão: converted_keras/labels.txt)
- `--interval`: Intervalo em segundos entre predições (padrão: 0.5)
- `--no-fps`: Não exibir FPS na tela

Exemplo:
```
python main.py --camera 1 --interval 0.2
```

## Funcionamento

1. O programa carrega o modelo de IA especificado.
2. Inicializa a câmera e começa a capturar frames.
3. Em intervalos regulares, o frame atual é processado pelo modelo de IA.
4. O resultado da classificação é exibido na tela junto com a confiança da predição.
5. Pressione 'q' para sair do programa.

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
- `__init__(camera_id, model)`: Inicializa a câmera
- `start()`: Inicia a câmera
- `stop()`: Libera os recursos da câmera
- `run_with_model(display_fps, prediction_interval)`: Executa a câmera com o modelo de IA