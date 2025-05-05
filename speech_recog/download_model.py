import os
import sys
import urllib.request
import zipfile
import shutil

def download_model():
    """
    Baixa e extrai o modelo pequeno de inglês para Vosk
    """
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = "vosk-model-small-en-us-0.15.zip"
    extract_dir = "vosk-model-small-en-us-0.15"
    target_dir = "model-en-us-small"
    
    # Obtém o diretório do script atual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Muda para o diretório do script
    os.chdir(script_dir)
    
    # Verifica se o modelo já existe
    if os.path.exists(target_dir):
        print(f"O modelo já existe em: {target_dir}")
        response = input("Deseja baixar novamente? (s/n): ")
        if response.lower() != 's':
            return
        
        # Remove o diretório existente
        shutil.rmtree(target_dir)
    
    print(f"Baixando modelo de {model_url}...")
    
    # Baixa o arquivo zip
    try:
        urllib.request.urlretrieve(model_url, zip_path)
    except Exception as e:
        print(f"Erro ao baixar o modelo: {e}")
        return
    
    print("Download concluído. Extraindo arquivos...")
    
    # Extrai o arquivo zip
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
    except Exception as e:
        print(f"Erro ao extrair o modelo: {e}")
        return
    
    # Renomeia o diretório extraído
    try:
        if os.path.exists(extract_dir):
            os.rename(extract_dir, target_dir)
    except Exception as e:
        print(f"Erro ao renomear o diretório: {e}")
        return
    
    # Remove o arquivo zip
    os.remove(zip_path)
    
    print(f"Modelo extraído com sucesso para: {target_dir}")
    print("Pronto para usar o reconhecimento de voz!")

if __name__ == "__main__":
    download_model() 