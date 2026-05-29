# Analise completa do MetabaseHospital e viabilidade na Vercel

## Resumo executivo

O repositorio atual nao e uma aplicacao web pronta para Vercel. Ele e um projeto de BI composto por:

- um `Dockerfile` que sobe a imagem oficial do Metabase;
- scripts Python para gerar dados hospitalares ficticios;
- scripts Python para carregar CSVs em um MySQL;
- arquivos CSV versionados;
- documentacao de deploy no Railway.

Conclusao principal: a Vercel nao consegue hospedar o Metabase real diretamente neste formato de forma estavel. O Metabase e uma aplicacao Java/JVM de processo persistente, normalmente executada via Docker ou JAR. A Vercel e uma plataforma serverless/frontend e nao executa imagens Docker como servicos web persistentes.

Se hoje existe uma URL da Vercel abrindo o Metabase, ha tres possibilidades tecnicas:

1. A Vercel esta apenas servindo uma pagina, iframe ou rewrite para outro Metabase hospedado fora dela.
2. Existe uma configuracao de deploy na Vercel que nao esta versionada neste repositorio.
3. O Metabase esta sendo iniciado por algum workaround dentro de Function/build, o que explica quedas intermitentes.

Na copia local analisada nao existem `vercel.json`, `.vercel/`, `package.json`, `api/`, `pages/`, `app/`, `next.config.*` ou `vite.config.*`. Portanto, a configuracao real da Vercel nao esta representada no repositorio atual.

O caminho mais proximo do objetivo e separar as responsabilidades:

- Vercel hospeda uma camada publica leve, como landing page, iframe/embed ou dashboard customizado.
- Metabase roda fora da Vercel, em um ambiente que aceite container ou processo Java persistente, como Railway, Render, Fly.io, VPS, Cloud Run ou Metabase Cloud.
- O banco MySQL permanece como servico externo.

Se a exigencia for "somente Vercel, sem outro host", entao a solucao deixa de ser Metabase real e passa a ser um dashboard proprio, estatico ou serverless, gerado a partir dos CSVs ou de uma API leve.

## Inventario da aplicacao

### Estrutura encontrada

```text
MetabaseHospital/
  Dockerfile
  README.md
  RAILWAY.md
  railway.toml
  .env.example
  requirements/
    requirements.txt
  config/
    config.py
  src/
    Geradorbase.py
    inserirbanco.py
  csv_data/
    atendimentos.csv
    dispensacao_medicamentos.csv
    equipamentos_medicos.csv
    estoque_farmacia.csv
    funcionarios.csv
    hospitais.csv
    internacoes.csv
    itens_prescricao.csv
    leitos.csv
    manutencoes.csv
    medicamentos.csv
    nir_sac_registros.csv
    pacientes.csv
    prescricoes.csv
    setores.csv
  railway/
    metabase.env.example
    load-data.env.example
```

Nao ha `package.json`, `next.config.*`, `vite.config.*`, pasta `pages/`, pasta `app/` ou build frontend. Portanto a Vercel nao tem uma aplicacao frontend para detectar e publicar.

### Tamanho do repositorio

O repositorio e pequeno: cerca de 454 KB em arquivos versionados locais. O peso real nao esta nos CSVs nem nos scripts, mas no runtime do Metabase: imagem Docker, JVM, bibliotecas Java, inicializacao, migracoes internas e memoria em execucao.

### Dockerfile atual

```Dockerfile
FROM metabase/metabase:latest

ENV JAVA_OPTS="-Xmx768m"

EXPOSE 3000
```

Esse arquivo funciona para plataformas que rodam containers. Ele nao transforma o projeto em uma aplicacao Vercel, porque a Vercel nao executa Dockerfile como servico persistente.

## Pipeline de dados atual

```text
src/Geradorbase.py
  -> gera CSVs em csv_data/

src/inserirbanco.py
  -> le CSVs com pandas
  -> conecta no MySQL via SQLAlchemy/PyMySQL
  -> grava tabelas com pandas.to_sql(if_exists="replace")

MySQL HospitalDB
  -> armazena dados analiticos hospitalares

Metabase
  -> conecta no HospitalDB
  -> cria perguntas, graficos e dashboards

MySQL MetabaseDB
  -> armazena usuarios, dashboards e configuracoes internas do Metabase
```

## Arquivos CSV e volume de dados

| Arquivo | Linhas | Tamanho aprox. |
|---|---:|---:|
| atendimentos.csv | 500 | 93,4 KB |
| dispensacao_medicamentos.csv | 250 | 10,82 KB |
| equipamentos_medicos.csv | 50 | 6,02 KB |
| estoque_farmacia.csv | 100 | 6,99 KB |
| funcionarios.csv | 50 | 5,67 KB |
| hospitais.csv | 3 | 0,55 KB |
| internacoes.csv | 100 | 9,92 KB |
| itens_prescricao.csv | 300 | 24,78 KB |
| leitos.csv | 100 | 4,54 KB |
| manutencoes.csv | 30 | 6,21 KB |
| medicamentos.csv | 50 | 3,98 KB |
| nir_sac_registros.csv | 75 | 12,19 KB |
| pacientes.csv | 100 | 23,35 KB |
| prescricoes.csv | 200 | 8,43 KB |
| setores.csv | 15 | 0,56 KB |

Os dados sao leves. Eles caberiam facilmente em uma aplicacao estatica ou em um pequeno banco externo. O gargalo e hospedar o Metabase, nao hospedar os dados.

## Analise de dependencias

Arquivo: `requirements/requirements.txt`

```text
python-dotenv
pandas
Faker
pymysql
sqlalchemy
requests
cryptography
peewee
```

Uso real observado:

| Dependencia | Uso atual |
|---|---|
| python-dotenv | usada em `config/config.py` |
| pandas | usada em `Geradorbase.py` e `inserirbanco.py` |
| Faker | usada em `Geradorbase.py` |
| pymysql | usada pelo SQLAlchemy na URL `mysql+pymysql` |
| sqlalchemy | usada em `config/config.py` e na carga |
| requests | nao encontrado uso no codigo atual |
| cryptography | nao encontrado uso direto no codigo atual |
| peewee | nao encontrado uso no codigo atual |

Recomendacao: se o objetivo for manter so geracao e carga de dados, avaliar remover `requests`, `cryptography` e `peewee`, salvo se alguma delas for exigida indiretamente pelo driver MySQL ou por uma etapa ainda nao versionada.

## Analise dos scripts

### `src/Geradorbase.py`

Responsabilidade:

- gerar dados ficticios hospitalares;
- salvar os CSVs em `csv_data/`;
- criar entidades como hospitais, pacientes, funcionarios, setores, leitos, medicamentos, atendimentos, internacoes, prescricoes, estoque, NIR/SAC e equipamentos.

Pontos fortes:

- cobre um dominio hospitalar rico;
- gera dados suficientes para demonstrar BI;
- mantem IDs consistentes o bastante para exploracao no Metabase;
- usa Faker `pt_BR`, o que melhora realismo dos dados.

Riscos e pontos de melhoria:

- ha comentarios dizendo "por hospital" ou "por setor", mas o codigo gera totais globais. Exemplo: `NUM_SETORES = 15` gera 15 setores no total, nao 15 por hospital.
- `medico_ids` e `farmaceutico_ids` dependem de sorteio aleatorio dos cargos. Em uma geracao futura, pode nao haver nenhum medico ou farmaceutico e `random.choice([])` quebraria a execucao.
- os dados sao ficticios, mas incluem campos com aparencia de CPF, RG, telefone e email. Para portfolio esta ok, mas a documentacao publica deve deixar claro que nao sao dados reais.
- nao ha seed fixa de randomizacao. Cada execucao gera dados diferentes, o que dificulta reproduzir exatamente os mesmos dashboards.

### `src/inserirbanco.py`

Responsabilidade:

- ler CSVs em uma ordem definida;
- carregar cada tabela no MySQL;
- usar `to_sql(..., if_exists="replace")`.

Pontos fortes:

- simples e facil de executar;
- respeita uma ordem logica de carga;
- funciona bem para demo ou portfolio.

Riscos e pontos de melhoria:

- `if_exists="replace"` apaga e recria cada tabela. Isso e destrutivo.
- as tabelas criadas pelo `pandas.to_sql` nao recebem chaves estrangeiras, indices ou tipos otimizados de forma explicita.
- a ordem de carga ajuda visualmente, mas nao garante integridade relacional no banco.
- nao ha transacao unica para rollback completo se uma tabela falhar depois de outras terem sido substituidas.
- erros sao impressos, mas nao encerram o processo com falha. Isso pode dar uma falsa sensacao de sucesso.

### `config/config.py`

Responsabilidade:

- carregar variaveis de ambiente;
- aceitar nomes locais (`HOST`, `DATABASE`, `USER_DB`, `PASSWORD_DB`, `PORT`) e nomes Railway/MySQL (`MYSQLHOST`, `MYSQLDATABASE`, etc.);
- criar `ENGINEH` do SQLAlchemy.

Pontos fortes:

- flexivel para ambiente local e Railway;
- falha cedo quando variavel obrigatoria esta ausente;
- valida porta como inteiro.

Riscos e pontos de melhoria:

- usa `PORT` como alternativa para porta do banco. Em plataformas web, `PORT` normalmente representa a porta HTTP do servico. Isso pode causar conflito se o script rodar em ambiente que tambem define `PORT` para web.
- o objeto `ENGINEH` e criado no import. Isso e simples, mas reduz controle em testes.

## Por que a Vercel nao hospeda o Metabase real diretamente

### 1. Vercel nao roda Docker como servico

O projeto atual depende de:

```Dockerfile
FROM metabase/metabase:latest
```

A Vercel informa em sua documentacao que nao suporta deploy direto de imagens Docker e que nao executa instancias Docker como runtime de aplicacao. Docker pode ser usado localmente para desenvolvimento, mas nao como formato de deploy na Vercel.

Impacto neste projeto:

- o `Dockerfile` atual e adequado para Railway/Render/Fly/VPS;
- o `Dockerfile` atual nao e um caminho de deploy para Vercel;
- importar este repositorio na Vercel nao sobe o Metabase.

### 2. Metabase e uma aplicacao Java persistente

O Metabase e distribuido como imagem Docker ou arquivo Java JAR. Ele sobe um servidor web proprio, normalmente na porta 3000, executa migracoes, mantem conexoes com banco e precisa de um banco de aplicacao para guardar usuarios, perguntas, dashboards e configuracoes.

Isso conflita com o modelo serverless da Vercel:

- uma Function nao e um processo web permanente;
- nao ha como abrir e manter um servidor Jetty/Metabase escutando porta 3000 dentro de uma Function;
- cold start de JVM + Metabase seria pesado e instavel;
- o bundle e as dependencias do Metabase tendem a exceder o perfil esperado de uma Function;
- o filesystem de Function nao deve ser usado como banco interno H2 persistente.

### 3. Limites de Function nao resolvem o problema

Mesmo que a memoria maxima de uma Function possa parecer suficiente em alguns planos, o problema nao e so memoria. O problema e o modelo de execucao:

- Metabase precisa ser um processo HTTP de longa duracao;
- Vercel Functions respondem a requisicoes individuais;
- Metabase precisa de inicializacao, migracoes, conexoes e estado de aplicacao;
- dashboards interativos dependem de varias rotas internas, assets e sessao.

Portanto, "aumentar memoria" na Vercel nao transforma Metabase em uma aplicacao Vercel.

## O que da para hospedar na Vercel

### Opcao A - Vercel como portal/embed, Metabase fora da Vercel

Arquitetura recomendada se a exigencia for usar Metabase real:

```text
Usuario
  -> Vercel: pagina publica leve
      -> iframe/embed publico do Metabase
          -> Metabase em Railway/Render/Fly/VPS/Cloud Run/Metabase Cloud
              -> HospitalDB MySQL
              -> MetabaseDB MySQL/Postgres
```

Vantagens:

- mantem Metabase real;
- Vercel fica leve;
- melhor chance de estabilidade;
- separa frontend publico do BI pesado.

Desvantagens:

- ainda existe um host externo para o Metabase;
- embed publico precisa ser configurado com cuidado;
- se o Metabase externo cair, a pagina Vercel tambem perde o dashboard embutido.

### Opcao B - Recriar dashboard leve na Vercel, sem Metabase

Arquitetura recomendada se a exigencia for "somente Vercel":

```text
CSV ou MySQL externo
  -> script de build gera JSON agregado
  -> Vercel hospeda dashboard React/Next/Vite
  -> graficos com Recharts/ECharts/Chart.js
```

Vantagens:

- roda muito bem na Vercel;
- extremamente leve;
- sem JVM, sem Docker, sem MetabaseDB;
- custo menor;
- ideal para portfolio publico.

Desvantagens:

- nao e Metabase real;
- perde criacao visual de perguntas/dashboards dentro do Metabase;
- precisa implementar filtros, graficos e KPIs no codigo.

### Opcao C - Metabase Cloud

Arquitetura:

```text
Usuario
  -> Vercel: pagina publica ou institucional
      -> link/embed do Metabase Cloud
          -> MySQL externo com dados hospitalares
```

Vantagens:

- Metabase real;
- sem operacao de container;
- melhor estabilidade.

Desvantagens:

- custo do Metabase Cloud;
- menos controle de infraestrutura.

## Decisao recomendada

Para manter Metabase real: nao tentar hospedar o Metabase na Vercel. Use Vercel como camada publica e hospede Metabase em uma plataforma de container/processo persistente.

Para usar apenas Vercel: trocar o objetivo tecnico de "hospedar Metabase" para "hospedar um dashboard hospitalar equivalente". Nesse caso, o projeto deve ganhar um frontend proprio e os CSVs podem virar JSONs agregados no build.

## Plano pratico 1: manter Metabase real

1. Pin de versao no Dockerfile:

```Dockerfile
FROM metabase/metabase:v0.xx.x
```

Evitar `latest`, porque uma atualizacao automatica pode quebrar o deploy.

2. Hospedar Metabase em Railway, Render, Fly.io, VPS ou Cloud Run.

3. Configurar banco interno do Metabase:

```env
MB_DB_TYPE=mysql
MB_DB_HOST=...
MB_DB_PORT=...
MB_DB_DBNAME=...
MB_DB_USER=...
MB_DB_PASS=...
```

4. Configurar banco analitico HospitalDB no Metabase.

5. Criar dashboards no Metabase.

6. Ativar compartilhamento publico ou signed embedding conforme necessidade.

7. Criar um frontend Vercel minimo que mostra:

- nome do projeto;
- contexto do dashboard;
- iframe/embed do Metabase;
- fallback se o Metabase estiver indisponivel.

## Plano pratico 2: Vercel 100%, sem Metabase

1. Criar uma pasta `web/` com Next.js ou Vite.

2. Criar script de build:

```text
csv_data/*.csv -> public/data/*.json
```

3. Gerar KPIs agregados:

- total de atendimentos;
- tempo medio de espera;
- taxa de ocupacao de leitos;
- internacoes ativas;
- atendimentos por gravidade;
- dispensacoes por medicamento;
- incidentes NIR/SAC por severidade;
- custo de manutencao por equipamento;
- estoque abaixo do minimo.

4. Renderizar graficos no frontend.

5. Deploy na Vercel apontando para a pasta `web/`.

6. Opcional: manter MySQL externo para dados dinamicos e usar API routes serverless apenas para consultas leves.

## Plano pratico 3: monorepo com dois deploys

Estrutura sugerida:

```text
MetabaseHospital/
  metabase/
    Dockerfile
    railway.toml
  etl/
    src/
    requirements/
    csv_data/
  web/
    package.json
    src/
    public/
```

Deploys:

- `metabase/` vai para Railway/Render/Fly/VPS.
- `web/` vai para Vercel.
- `etl/` roda localmente, em CI ou como job agendado fora da Vercel.

Essa organizacao evita que a Vercel tente entender arquivos que nao pertencem a ela.

## Checklist para deixar o projeto mais leve

- [ ] Remover dependencias Python nao usadas.
- [ ] Separar codigo de ETL, Metabase e frontend.
- [ ] Trocar `metabase/metabase:latest` por versao fixa.
- [ ] Corrigir README/RAILWAY com encoding UTF-8 valido.
- [ ] Criar seed fixa no gerador de dados para demos reproduziveis.
- [ ] Tratar listas vazias de medicos/farmaceuticos no gerador.
- [ ] Trocar `if_exists="replace"` por fluxo mais seguro se houver dados reais.
- [ ] Criar DDL SQL com chaves primarias, indices e relacionamentos se o banco for mantido.
- [ ] Documentar que os dados sao ficticios.
- [ ] Decidir oficialmente entre "Metabase real fora da Vercel" e "dashboard proprio 100% Vercel".

## Riscos se tentar forcar Metabase na Vercel

- Deploy nao reconhecido por falta de app frontend.
- Dockerfile ignorado/incompativel com runtime da Vercel.
- Falha por falta de processo persistente.
- Cold start inviavel se tentar iniciar Java dentro de Function.
- Perda de dados se tentar usar H2 em filesystem efemero.
- Instabilidade em migracoes internas do Metabase.
- Dificuldade para servir assets e rotas internas do Metabase.

## Veredito

Nao ha ajuste pequeno neste repositorio que faca a Vercel hospedar o Metabase real com a mesma estabilidade de uma plataforma de container. A limitacao e de plataforma, nao apenas de organizacao do codigo.

O repositorio pode, sim, ser adaptado para uma experiencia muito leve na Vercel se uma destas duas decisoes for tomada:

1. Vercel hospeda apenas a camada publica e embute um Metabase externo.
2. Vercel hospeda um dashboard proprio que substitui o Metabase.

Se a decisao for manter a URL da Vercel a qualquer custo, a arquitetura mais estavel e usar a Vercel como camada de entrada/proxy e manter o processo Metabase em um runtime persistente por tras.

Para portfolio, a opcao 2 tende a ser a mais leve e controlavel. Para manter a experiencia do Metabase real, a opcao 1 e a mais correta.

## Referencias oficiais consultadas

- Vercel - Docker deployments: https://vercel.com/kb/guide/does-vercel-support-docker-deployments
- Vercel - Function limits: https://vercel.com/docs/functions/limitations
- Vercel - Platform limits: https://vercel.com/docs/limits
- Metabase - Installing Metabase: https://www.metabase.com/docs/latest/installation-and-operation/installing-metabase
- Metabase - Running Metabase on Docker: https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker
- Metabase - Application database: https://www.metabase.com/docs/latest/installation-and-operation/configuring-application-database
