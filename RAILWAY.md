# Deploy no Railway

Este projeto usa tres partes:

1. **HospitalDB**: banco MySQL com as tabelas geradas pelos CSVs.
2. **MetabaseDB**: banco MySQL separado para guardar usuarios, dashboards e configuracoes internas do Metabase.
3. **Metabase**: servico web publicado no Railway usando o `Dockerfile` deste repositorio.

> Da para usar um unico MySQL para tudo, mas nao e o ideal: as tabelas internas do Metabase ficam misturadas com os dados do BI.

## 1. Criar o projeto no Railway

1. Crie um novo projeto no Railway.
2. Adicione um banco MySQL e renomeie o servico para `HospitalDB`.
3. Adicione outro banco MySQL e renomeie o servico para `MetabaseDB`.
4. Adicione um novo servico a partir deste repositorio GitHub.

O Railway cria automaticamente estas variaveis no MySQL:

- `MYSQLHOST`
- `MYSQLPORT`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `MYSQLDATABASE`
- `MYSQL_URL`

Referencia: https://docs.railway.com/databases/mysql

## 2. Configurar o servico Metabase

No servico do Metabase, adicione as variaveis do arquivo:

```text
railway/metabase.env.example
```

Elas apontam o Metabase para o `MetabaseDB`, que sera o banco interno dele.

Variaveis principais:

```env
PORT=3000
MB_JETTY_PORT=3000
MB_JETTY_HOST=0.0.0.0
MB_SITE_NAME=Metabase Hospital
MB_SITE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
MB_LOAD_SAMPLE_CONTENT=false
JAVA_OPTS=-Xmx768m

MB_DB_TYPE=mysql
MB_DB_HOST=${{MetabaseDB.MYSQLHOST}}
MB_DB_PORT=${{MetabaseDB.MYSQLPORT}}
MB_DB_DBNAME=${{MetabaseDB.MYSQLDATABASE}}
MB_DB_USER=${{MetabaseDB.MYSQLUSER}}
MB_DB_PASS=${{MetabaseDB.MYSQLPASSWORD}}
```

Depois, gere um dominio publico no servico Metabase em **Settings > Networking**.

Referencia das variaveis do Metabase: https://www.metabase.com/docs/latest/configuring-metabase/environment-variables

Depois que o Metabase estiver no ar e conectado ao `HospitalDB`, siga o guia de embed para publicar o dashboard no seu site:

```text
docs/GUIA_EMBED_SITE.md
```

## 3. Carregar os CSVs no HospitalDB

No seu computador, instale as dependencias:

```powershell
python -m pip install -r requirements/requirements.txt
```

Gere os CSVs:

```powershell
python src/Geradorbase.py
```

Para carregar no banco do Railway, preencha o `.env` com os dados do `HospitalDB`.

Se estiver rodando localmente, use o **TCP Proxy** do Railway para `MYSQLHOST` e `MYSQLPORT`, porque o host privado do Railway so funciona entre servicos dentro do mesmo projeto.

Exemplo:

```env
MYSQLHOST=<host-do-tcp-proxy>
MYSQLPORT=<porta-do-tcp-proxy>
MYSQLDATABASE=<database-do-HospitalDB>
MYSQLUSER=<usuario-do-HospitalDB>
MYSQLPASSWORD=<senha-do-HospitalDB>
```

Carregue os dados:

```powershell
python src/inserirbanco.py
```

Referencia do TCP Proxy: https://docs.railway.com/networking/tcp-proxy

## 4. Conectar o BI no Metabase

1. Abra a URL publica do Metabase.
2. Crie o usuario administrador.
3. Va em **Admin settings > Databases > Add database**.
4. Escolha **MySQL**.
5. Use os dados do `HospitalDB`:
   - Host: valor de `MYSQLHOST` do `HospitalDB`
   - Port: valor de `MYSQLPORT`
   - Database name: valor de `MYSQLDATABASE`
   - Username: valor de `MYSQLUSER`
   - Password: valor de `MYSQLPASSWORD`
6. Crie as perguntas, dashboards e habilite compartilhamento publico ou embed conforme necessario.

## Checklist rapido

- `HospitalDB` criado no Railway.
- `MetabaseDB` criado no Railway.
- Servico Metabase criado a partir do GitHub.
- Variaveis `MB_DB_*` configuradas no servico Metabase.
- Dominio publico gerado no Railway.
- CSVs gerados localmente.
- `.env` local apontando para o `HospitalDB` via TCP Proxy.
- `python src/inserirbanco.py` executado com sucesso.
- Banco `HospitalDB` adicionado como fonte de dados dentro do Metabase.

## Erro: Railway tentou usar Python/Railpack

Se aparecer uma mensagem parecida com:

```text
Move requirements.txt to the repo root so Railpack can detect this as a Python project
```

o Railway tentou adivinhar o projeto como Python. Para este servico, isso esta errado: o deploy web deve usar o Metabase via `Dockerfile`.

Confira estes pontos:

1. O arquivo `Dockerfile` precisa estar na raiz do repositorio.
2. O arquivo `railway.toml` precisa estar na raiz do repositorio.
3. No Railway, em **Settings > Source**, o **Root Directory** deve estar vazio ou `/`.
4. Depois de commitar e dar push, rode **Redeploy**.

O `railway.toml` deste projeto força:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "/Dockerfile"
```

## Erro: Java heap space / OutOfMemory

Se os logs mostrarem:

```text
Maximum memory available to JVM: 232.0 MB
java.lang.OutOfMemoryError: Java heap space
```

o servico do Metabase esta com pouca memoria. O Metabase precisa de pelo menos 1 GB de RAM para iniciar com estabilidade em producao.

Em um container com 1 GB, o Java pode reservar automaticamente so uma parte da memoria para heap. Se o log mostrar `Maximum memory available to JVM: 232.0 MB`, adicione esta variavel ao servico `MetabaseHospital`:

```env
JAVA_OPTS=-Xmx768m
```

Como corrigir:

1. No Railway, abra o servico `MetabaseHospital`.
2. Aumente o limite de memoria/plano do servico para pelo menos 1 GB.
3. Adicione `JAVA_OPTS=-Xmx768m` em **Variables**.
4. Confira as variaveis `MB_DB_*` em **Variables** para garantir que o Metabase esta usando o `MetabaseDB`, e nao o H2 interno.
5. Rode **Redeploy**.

Se aparecer tambem:

```text
Using Metabase with an H2 application database is not recommended for production deployments
```

as variaveis do banco interno do Metabase ainda nao foram configuradas ou nao foram aplicadas ao deploy atual.
