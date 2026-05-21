# Metabase Hospital

O **MetabaseHospital** é um projeto que demonstra uma solução de pipeline de dados e dashboard analítico para o setor de saúde. O objetivo é gerar dados fictícios, armazená-los em um banco MySQL e criar KPIs que façam sentido no quesito de hospitais usando Metabase.

##  Funcionalidades

* **Geração de dados fictícios** em Python, simulando tabelas como hospitais, pacientes, funcionários, atendimentos, internações, prescrições, entre outras.
* Carga dos arquivos CSV gerados para um banco MySQL, respeitando relacionamentos e chaves estrangeiras.
* **Dashboard interativo** no Metabase explorando KPIs hospitalares e indicadores de operação.
* **Embed público** do dashboard para exibição.
* **Deploy no Railway** com MySQL + Metabase.

##  Objetivos do Projeto

1. Demonstrar habilidades em geração e manipulação de dados.
2. Construir um pipeline confiável de ETL (Extract, Transform, Load) com Python e SQLAlchemy.
3. Configurar serviços em MySQL + Metabase.
4. Criar relatórios e gráficos interativos para análise de métricas hospitalares.

##  Como Executar

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/MetabaseHospital.git
   ```
2. Copie o arquivo `.env.example` para `.env` e preencha as variáveis de conexão ao MySQL: `HOST`, `DATABASE`, `USER_DB`, `PASSWORD_DB`, `PORT`.
3. Instale dependências e gere os dados fictícios:

   ```bash
   pip install -r requirements/requirements.txt
   python src/Geradorbase.py
   ```
4. Carregue os CSVs no banco:

   ```bash
   python src/inserirbanco.py
   ```
5. Acesse o Metabase no seu servidor + porta, crie seu dashboard e utilize o recurso de embed para compartilhar ou compartilhe o link diretamente.

## Deploy no Railway

Para hospedar o banco MySQL e o Metabase no Railway, siga o guia:

```text
RAILWAY.md
```

---

> Feito por Matheus — Analista e Engenheiro de Dados.
