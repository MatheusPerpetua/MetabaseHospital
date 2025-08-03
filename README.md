# Metabase Hospital

O **MetabaseHospital** é um projeto que demonstra uma solução de pipeline de dados e dashboard analítico para o setor de saúde. O objetivo é gerar dados fictícios, armazená-los em um banco MySQL e criar KPIs que façam sentido no quesito de hospitais usando Metabase.

##  Funcionalidades

* **Geração de dados fictícios** em Python, simulando tabelas como hospitais, pacientes, funcionários, atendimentos, internações, prescrições, entre outras.
* Carga dos arquivos CSV gerados para um banco MySQL, respeitando relacionamentos e chaves estrangeiras.
* **Dashboard interativo** no Metabase explorando KPIs hospitalares e indicadores de operação.
* **Embed público** do dashboard para exibição.

##  Objetivos do Projeto

1. Demonstrar habilidades em geração e manipulação de dados.
2. Construir um pipeline confiável de ETL (Extract, Transform, Load) com Python e SQLAlchemy.
3. Configurar serviços em MySQL + Metabase.
4. Criar relatórios e gráficos interativos para análise de métricas hospitalares.

##  Como Executar

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/MetabaseHospital.git
   cd MetabaseHospital
   ```
2. Configure as variáveis de ambiente no arquivo `.env` com as seguintes chaves para conexão ao MySQL: `HOST`, `DATABASE`, `USER_DB`, `PASSWORD_DB`, `PORT`.
3. Instale dependências e gere os dados fictícios:

   ```bash
   pip install -r requirements.txt
   python Geradorbase.py
   ```
4. Carregue os CSVs no banco:

   ```bash
   python inserirbanco.py
   ```
5. Acesse o Metabase em (link do embed do metabasee), crie seu dashboard e utilize o recurso de embed para compartilhar.

---

> Feito por Matheus — Analista e Engenheiro de Dados.
