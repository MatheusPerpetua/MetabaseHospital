# Este script lê arquivos CSV da pasta 'csv_data' e os carrega
# para o banco de dados MYSQL usando SQLAlchemy e pandas.
#
# --- IMPORTAÇÕES ---
import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))

import pandas as pd
from config import ENGINEH

# --- PARTE 2: CARREGAMENTO DE DADOS NO BANCO DE DADOS ---

if __name__ == "__main__":
    print("--- INICIANDO CARREGAMENTO DE DADOS NO BANCO DE DADOS ---")
    
    # Ordem de carregamento para respeitar chaves estrangeiras
    table_load_order = [
        'hospitais', 'pacientes', 'medicamentos', 'funcionarios',
        'setores', 'leitos', 'estoque_farmacia', 'atendimentos',
        'internacoes', 'prescricoes', 'itens_prescricao',
        'dispensacao_medicamentos', 'nir_sac_registros',
        'equipamentos_medicos', 'manutencoes'
    ]

    # Função para inserir dados no banco de dados usando pandas.to_sql()
    def insert_data_to_db(table_name, df, engine):
        print(f"Inserindo dados para a tabela: {table_name}")
        try:
            # Use 'append' para adicionar registros à tabela existente.
            # O 'index=False' evita que o índice do DataFrame seja salvo como uma coluna.
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            print(f"Concluída a inserção para {table_name}.")
        except Exception as e:
            print(f"Erro ao inserir dados na tabela {table_name}: {e}")

    # O ENGINE é importado do seu arquivo de configuração `config.py`
    engine_db = ENGINEH

    # O loop para carregar os dados no banco
    for table_name in table_load_order:
        csv_path = os.path.join('csv_data', f'{table_name}.csv')
        if os.path.exists(csv_path):
            try:
                # O 'low_memory=False' ajuda a evitar problemas de tipo de dados em arquivos grandes
                df = pd.read_csv(csv_path)
                insert_data_to_db(table_name, df, engine_db)
            except Exception as e:
                print(f"Erro ao ler ou processar o arquivo CSV {csv_path}: {e}")
        else:
            print(f"Arquivo CSV não encontrado: {csv_path}. Certifique-se de que os arquivos foram gerados.")
    
    print("\n--- PROCESSO DE CARREGAMENTO DE DADOS CONCLUÍDO ---")
