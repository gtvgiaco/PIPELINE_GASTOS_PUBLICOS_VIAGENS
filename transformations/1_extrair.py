"""
1_extrair.py  -  FASE 1: Extracao e Camada RAW
----------------------------------------------
Passo a passo simples:
  1. Localiza o arquivo viagens no google que foi baixado para a pasta data/.
  2. Le os 4 CSVs de dentro do .zip vendas, itens).
  3. Insere os dados, SEM nenhuma alteracao, nas 4 tabelas RAW do MySQL.

A camada RAW e uma copia fiel do CSV: todas as colunas sao texto (VARCHAR).
"""

import zipfile # abrir e ler arquivos .zip. Nao precisa descompactar no disco rigido
import gdown # serve para baixar arquivos hospedados no google drive.

import pandas as pd # leitura do csv em chunks

import config 
import banco

# 1. baixar o arquivo zip do drive
def baixar_zip():
    config.PASTA_DADOS.mkdir(exist_ok=True) #cria uma pasta no pc se ainda nao existir.
    destino = config.PASTA_DADOS / "viagens.zip" #busca o arquivo no google drive, baixa e coloca dentro da pasta criada.

    if destino.exists():
        print("[1/3] O arquivo já foi baixado antes - pulando o download.")
    else:
        print("[1/3] Baixando o aqruivo do google drive.")
        gdown.download(id=config.DRIVE_FILE_ID, output=str(destino))
    return destino

#2. Carregar os dados dos arquivos CSV nas tabelas raw
def carregar_csv(conexao, zip_aberto, nome_csv, tabela):
    '''Le um CSV dentro do zip e insere todas as linhas na tabela do MySQL.
    
    As colunas do CSV estao na mesma ordem das colunas da tabela (definiddas no 0_criar_banco.sql)
    Por isso conseguimos inserir na ordem sem precisar escrever o nome de cada coluna'''
    print("Carregando", tabela, "...")

    #esvazia a tabela antes de carregar, para nao duplicar dados ao rodar novamente.
    banco.executar(conexao, f"TRUNCATE TABLE {tabela}")

    total = 0
    with zip_aberto.open(nome_csv) as arquivo:
        #lê o csv em pedaços (chunks), para não sobrecarregar a memória em bases grandes.
        pedacos = pd.read_csv(
            arquivo,
            sep=config.CSV_SEPARADOR, #colunas separadas por ;
            encoding=config.CSV_ENCODING, #acentuação em latin-1
            dtype=str, #tipo texto para todas as colunas (camada raw)
            keep_default_na=False, #campo vazio permanece vazio (nao vira "NaN")
            chunksize=config.TAMANHO_BLOCO, 
        )
        for pedaco in pedacos:
            linhas = pedaco.values.tolist()
            marcadores = ",".join(["%s"] * len(pedaco.columns)) #uma %s para cada coluna do CSV
            comando = f'INSERT INTO {tabela} VALUES ({marcadores})'
            banco.inserir_em_lote(conexao, comando, linhas)
            total += len(linhas)

    print("->", total, "linhas em", tabela)

#3. Programa principal
def main():
    print('FASE 1: EXTRACAO + CAMADA RAW')
    try:
        conexao = banco.conectar()

        caminho_zip = baixar_zip()
        print("[2/3] Abrindo o arquivo zip...")
        print("[3/3] Carregando as 4 tabelas RAW...")
        with zipfile.ZipFile(caminho_zip) as zip_aberto:
            for arquivo in config.ARQUIVOS.values():
                carregar_csv(conexao, zip_aberto, arquivo["csv"], arquivo["tabela_raw"])

        conexao.close()
        print("=== Camada RAW concluida com sucesso! ===")
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)
        raise


if __name__ == "__main__":
    main()
