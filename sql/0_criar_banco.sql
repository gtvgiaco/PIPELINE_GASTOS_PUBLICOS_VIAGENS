-- 1. Criar o banco de dados.
CREATE DATABASE IF NOT EXISTS transparencia
	CHARACTER SET utf8mb4 -- suporta caracteres especiais
	COLLATE utf8mb4_general_ci;

USE transparencia;

-- 2. Criação das tabelas raw.

-- 2.1 tabela raw_viagem
DROP TABLE IF EXISTS raw_viagem;
CREATE TABLE raw_viagem (
	identificador_do_processo_de_viagem VARCHAR(20),
    numero_da_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    justificativa_urgencia_viagem VARCHAR(4000),
    codigo_do_orgao_superior VARCHAR(20),
    nome_do_orgao_superior VARCHAR(255),
    codigo_orgao_solicitante VARCHAR(20),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante VARCHAR(15),
    nome VARCHAR(255),
    cargo VARCHAR(255),
    funcao VARCHAR(255),
    descricao_funcao VARCHAR(255),
    periodo_data_de_inicio VARCHAR(10),
    periodo_data_de_fim VARCHAR(10),
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias VARCHAR(10),
    valor_passagens VARCHAR(10),
    valor_devolucao VARCHAR(10),
	valor_outros_gastos VARCHAR(10)
)ENGINE=InnoDB -- é o mecanismo de armazenamento padrão e mais robusto.
ROW_FORMAT=DYNAMIC; 

-- 2.2 tabela raw_pagamento
DROP TABLE IF EXISTS raw_pagamento;
CREATE TABLE raw_pagamento (
	identificador_do_processo_de_viagem VARCHAR(20),
    numero_da_proposta VARCHAR(20),
    codigo_do_orgao_superior VARCHAR(20),
    nome_do_orgao_superior VARCHAR(255),
    codigo_do_orgao_pagador VARCHAR(20),
    nome_do_orgao_pagador VARCHAR(255),
    codigo_da_unidade_gestora_pagadora VARCHAR(20),
    nome_da_unidade_gestora_pagadora VARCHAR(255),
    tipo_de_pagamento VARCHAR(50),
    valor VARCHAR(20)
) ENGINE=InnoDB;

-- 2.3 tabela raw_passagem
DROP TABLE IF EXISTS raw_passagem;
CREATE TABLE raw_passagem (
	identificador_do_processo_de_viagem VARCHAR(20),
    numero_da_proposta_pcdp VARCHAR(20),
    meio_de_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    pais_origem_volta VARCHAR(60),
    uf_origem_volta VARCHAR(40),
    cidade_origem_volta VARCHAR(80),
    pais_destino_volta VARCHAR(60),
    uf_destino_volta VARCHAR(40),
    cidade_destino_volta VARCHAR(80),
    valor_da_passagem VARCHAR(20),
    taxa_de_servico VARCHAR(20),
    data_da_emissao_compra VARCHAR(10),
    hora_da_emissao_compra VARCHAR(10)
)ENGINE=InnoDB;

-- 2.4 Tabela raw_trecho
DROP TABLE IF EXISTS raw_trecho;
CREATE TABLE raw_trecho (
	identificador_do_processo_de_viagem VARCHAR(20),
    numero_da_proposta_pcdp VARCHAR(20),
    sequencia_trecho VARCHAR(20),
    origem_data VARCHAR(10),
    origem_pais VARCHAR(60),
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data VARCHAR(10),
    destino_pais VARCHAR(60),
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_de_transporte VARCHAR(50),
    numero_diarias VARCHAR(10),
    missao VARCHAR(50)
)ENGINE=InnoDB;

-- 3. Criação das tabelas silver

-- 3.1 tabela silver_viagem
DROP TABLE IF EXISTS silver_viagem;
CREATE TABLE silver_viagem (
	id_viagem VARCHAR(20) NOT NULL PRIMARY KEY,
	num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2) CHECK(valor_diarias >=0),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2), -- coluna calculada
    duracao_dias INT -- coluna calculada
)ENGINE=InnoDB
ROW_FORMAT=DYNAMIC;

-- 3.2 tabela silver_passagem
DROP TABLE IF EXISTS silver_passagem;
CREATE TABLE silver_passagem (
	id_passagem INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2) CHECK(valor_passagem >= 0),
    taxa_servico DECIMAL(10,2) CHECK(taxa_servico >= 0),
    data_emissao DATE,
    FOREIGN KEY(id_viagem) REFERENCES silver_viagem(id_viagem)
)ENGINE=InnoDB;


-- 3.3 tabela silver_pagamento
DROP TABLE IF EXISTS silver_pagamento;
CREATE TABLE silver_pagamento (
	id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL,
    valor DECIMAL(10,2) CHECK(valor >=0),
    FOREIGN KEY(id_viagem) REFERENCES silver_viagem(id_viagem)
)ENGINE=InnoDB;

-- 3.4 tabela silver_trecho
DROP TABLE IF EXISTS silver_trecho;
CREATE TABLE silver_trecho (
	id_trecho INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2) CHECK(numero_diarias >=0),
    FOREIGN KEY(id_viagem) REFERENCES silver_viagem(id_viagem),
    CONSTRAINT id_viagem_sequencia UNIQUE(id_viagem, sequencia_trecho)
)ENGINE=InnoDB;    