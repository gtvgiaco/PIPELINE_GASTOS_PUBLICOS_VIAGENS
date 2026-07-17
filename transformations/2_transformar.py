'''Transformar os dados da camada RAW (tudo VARCHAR) e preenche as tabelas
SILVER (já criadas com PK e FK) com os dados limpos e tipados.
1- Esvaziar as tabelas SILVER (para nao duplicar se rodar novamente).
2- Copiar os dados da RAW para a SILVER, convertendo os tipos de algumas colunas.
3- Calculamos as colunas derivadas (valor_total, duracao_dias).
'''

import banco

#Passo 1: esvaziar as tabelas SILVER.
# (apagar as tabelas filhas antes da principal, devido as chaves estrangeiras).
LIMPAR_SILVER = [
    'DELETE FROM silver_passagem',
    'DELETE FROM silver_pagamento',
    'DELETE FROM silver_trecho',
    'DELETE FROM silver_viagem',
]

#Passo 2: Copiar da RAW para a SILVER convertendo os tipos.
# (silver_viagem é a tabela principal. Carregar primeiro)
SQL_VIAGEM = """
INSERT INTO silver_viagem (
    id_viagem, num_proposta, situacao, viagem_urgente, cod_orgao_superior, nome_orgao_superior,
    nome_viajante, cargo, data_inicio, data_fim, destinos, motivo, valor_diarias, valor_passagens,
    valor_devolucao, valor_outros_gastos
)
SELECT
    identificador_do_processo_de_viagem,
    numero_da_proposta,
    situacao, 
    viagem_urgente,
    codigo_do_orgao_superior,
    nome_do_orgao_superior,
    nome,
    cargo,
    STR_TO_DATE(NULLIF(TRIM(periodo_data_de_inicio), ' '), '%d/%m/%Y'), 
    STR_TO_DATE(NULLIF(TRIM(periodo_data_de_fim), ' '), '%d/%m/%Y'),
    destinos, 
    motivo,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_diarias), ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_passagens),''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_devolucao),    ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_outros_gastos),    ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_viagem
"""

SQL_PAGAMENTO = """
INSERT INTO silver_pagamento (
    id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
    tipo_pagamento, valor
)
SELECT
    identificador_do_processo_de_viagem,
    numero_da_proposta,
    nome_do_orgao_pagador,
    nome_da_unidade_gestora_pagadora,
    tipo_de_pagamento,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor),    ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_pagamento
WHERE identificador_do_processo_de_viagem IN (SELECT id_viagem FROM silver_viagem)
"""

SQL_PASSAGEM = """
INSERT INTO silver_passagem (
    id_viagem, meio_transporte, pais_origem_ida, cidade_origem_ida,
    pais_destino_ida, uf_destino_ida, cidade_destino_ida, valor_passagem, 
    taxa_servico, data_emissao
)
SELECT
    identificador_do_processo_de_viagem,
    meio_de_transporte,
    pais_origem_ida,
    cidade_origem_ida,
    pais_destino_ida,
    uf_destino_ida,
    cidade_destino_ida,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(valor_da_passagem),    ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    CAST(REPLACE(REPLACE(NULLIF(TRIM(taxa_de_servico),    ''), '.', ''), ',', '.') AS DECIMAL(10,2)),
    STR_TO_DATE(NULLIF(TRIM(data_da_emissao_compra), ' '), '%d/%m/%Y')
FROM raw_passagem
WHERE identificador_do_processo_de_viagem IN (SELECT id_viagem FROM silver_viagem)
"""

SQL_TRECHO = """
INSERT INTO silver_trecho (
    id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
    destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias   
)
SELECT
    identificador_do_processo_de_viagem,
    sequencia_trecho,
    STR_TO_DATE(NULLIF(TRIM(origem_data), ' '), '%d/%m/%Y'), 
    origem_uf,
    origem_cidade,
    STR_TO_DATE(NULLIF(TRIM(destino_data), ' '), '%d/%m/%Y'),
    destino_uf,
    destino_cidade,
    meio_de_transporte,
    CAST(REPLACE(REPLACE(NULLIF(TRIM(numero_diarias),    ''), '.', ''), ',', '.') AS DECIMAL(10,2))
FROM raw_trecho
WHERE identificador_do_processo_de_viagem IN (SELECT id_viagem FROM silver_viagem)
"""

#PASSO 3. Calcular as colunas valor_total e duracao_dias
SQL_VALOR_TOTAL = """
UPDATE silver_viagem
SET valor_total = COALESCE(valor_diarias, 0) + COALESCE(valor_passagens, 0)
+ COALESCE(valor_devolucao, 0) + COALESCE(valor_outros_gastos, 0),
    duracao_dias = DATEDIFF(data_fim, data_inicio)
"""

def main():
    print("TRANSFORMAÇÃO DE TIPOS + COLUNAS CALCULADAS = CAMADA SILVER")
    try:
        conexao = banco.conectar()

        print("[1/3] Esvaziando as tabelas SILVER...")
        for comando in LIMPAR_SILVER:
            banco.executar(conexao, comando)

        print("[2/3] Copiando e convertendo RAW -> SILVER...")
        banco.executar(conexao, SQL_VIAGEM)
        print("      silver_viagem OK")
        banco.executar(conexao, SQL_PAGAMENTO)
        print("      silver_pagamento  OK")
        banco.executar(conexao, SQL_PASSAGEM)
        print("      silver_passagem  OK")
        banco.executar(conexao, SQL_TRECHO)
        print("      silver_trecho  OK")

        print("[3/3] Calculando valor_total e  duracao_dias...")
        banco.executar(conexao, SQL_VALOR_TOTAL)
        
        conexao.close()
        print("=== Camada SILVER concluida com sucesso! ===")
    except Exception as erro:
        print("[ERRO] Algo deu errado:", erro)
        raise


if __name__ == "__main__":
    main()