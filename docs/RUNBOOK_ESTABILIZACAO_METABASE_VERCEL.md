# Runbook de estabilizacao do Metabase mantendo Vercel

## Objetivo

Manter a experiencia atual com URL/domino na Vercel, reduzindo quedas do Metabase.

Este runbook assume a restricao informada: hoje o Metabase abre por uma URL da Vercel e a intencao e manter assim. A analise do repositorio local, porem, nao encontrou configuracao Vercel versionada. Isso significa que a causa das quedas provavelmente esta na configuracao externa da Vercel, nos limites de runtime, no servico real por tras da URL ou na forma como o Metabase esta sendo iniciado.

## Diagnostico rapido

Antes de mexer em codigo, identificar qual destes cenarios e o real:

### Cenario 1 - Vercel como proxy ou iframe

Sinais:

- existe uma pagina na Vercel que embute o Metabase em iframe;
- existe `vercel.json` com `rewrites` para uma URL externa;
- o Metabase de verdade roda em Railway, Render, Fly.io, VPS, Cloud Run ou Metabase Cloud;
- os logs da Vercel mostram poucas requisicoes reais de app e muitas respostas estaticas/proxy.

Esse e o melhor cenario para manter a Vercel, porque a Vercel fica leve e o Metabase roda onde ele foi feito para rodar.

### Cenario 2 - Metabase iniciado dentro da Vercel

Sinais:

- ha uma Function tentando baixar/rodar `metabase.jar`;
- o build ou a Function instala Java;
- erros aparecem como timeout, cold start, memoria, `FUNCTION_INVOCATION_FAILED`, `504`, `500`, processo morto ou bundle grande;
- a primeira abertura apos algum tempo demora muito ou falha.

Esse e o cenario mais instavel. Pode ate funcionar por periodos curtos, mas nao e uma base confiavel para Metabase.

### Cenario 3 - Deploy Vercel nao esta neste repositorio

Sinais:

- este repositorio nao tem `vercel.json`, `.vercel/`, `package.json`, `api/`, `pages/` ou `app/`;
- o projeto no painel da Vercel aponta para outra pasta, outro repositorio ou uma configuracao manual;
- o dominio esta na Vercel, mas o runtime real pode estar em outro lugar.

Esse e o que a copia local sugere. Para corrigir quedas, sera necessario consultar o painel/logs da Vercel e o servico apontado pelo dominio.

## O que verificar no painel da Vercel

1. Abra o projeto na Vercel.
2. Va em **Settings > Git** e confirme:
   - repositorio conectado;
   - branch;
   - root directory.
3. Va em **Settings > Build & Development Settings** e confirme:
   - framework detectado;
   - install command;
   - build command;
   - output directory.
4. Va em **Deployments > ultimo deploy > Logs** e procure:
   - erro de build;
   - timeout;
   - memoria;
   - function crash;
   - bundle size;
   - falta de variavel de ambiente.
5. Va em **Functions** ou logs runtime e procure:
   - codigos `500`, `502`, `504`;
   - `FUNCTION_INVOCATION_FAILED`;
   - `FUNCTION_PAYLOAD_TOO_LARGE`;
   - `Exceeded maximum duration`;
   - `Out of memory`;
   - `Java heap space`.

## Variaveis criticas do Metabase

Se o Metabase real estiver rodando em qualquer ambiente, estas variaveis precisam estar corretas:

```env
MB_SITE_NAME=Metabase Hospital
MB_SITE_URL=https://seu-dominio.vercel.app
MB_LOAD_SAMPLE_CONTENT=false

MB_DB_TYPE=mysql
MB_DB_HOST=...
MB_DB_PORT=3306
MB_DB_DBNAME=...
MB_DB_USER=...
MB_DB_PASS=...

JAVA_OPTS=-Xmx768m
```

### Crash ao conectar no MetabaseDB

Sintoma nos logs:

```text
Metabase Initialization FAILED
Unable to connect to Metabase mysql DB
RSA public key is not available client side
```

Esse erro acontece antes do Metabase subir a interface. Ele aponta para o banco interno do Metabase, nao para o `HospitalDB` dos dados analiticos.

Correcao recomendada no Railway:

```env
MB_DB_TYPE=mysql
MB_DB_CONNECTION_URI=jdbc:mysql://${{MetabaseDB.MYSQLHOST}}:${{MetabaseDB.MYSQLPORT}}/${{MetabaseDB.MYSQLDATABASE}}?allowPublicKeyRetrieval=true
MB_DB_USER=${{MetabaseDB.MYSQLUSER}}
MB_DB_PASS=${{MetabaseDB.MYSQLPASSWORD}}
```

Depois de salvar as variaveis, faca redeploy ou restart do servico Metabase.

Pontos importantes:

- Nao usar H2 em producao.
- Usar banco interno separado para o Metabase.
- Usar banco analitico separado para os dados hospitalares.
- Evitar `metabase/metabase:latest`; preferir versao fixa.
- `MB_SITE_URL` deve ser a URL publica final usada pelo usuario.

## Arquitetura recomendada mantendo a Vercel

```text
Usuario
  -> Dominio/URL na Vercel
      -> pagina leve, iframe ou rewrite
          -> Metabase em runtime persistente
              -> MetabaseDB
              -> HospitalDB
```

Essa arquitetura mantem a Vercel na frente, mas tira da Vercel o trabalho pesado de manter JVM, Jetty, Metabase e conexoes persistentes.

### Exemplo de `vercel.json` para proxy

Use apenas se houver uma URL externa estavel do Metabase:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "https://SEU-METABASE-EXTERNO.com/$1"
    }
  ]
}
```

Observacoes:

- Substituir `https://SEU-METABASE-EXTERNO.com` pela URL real.
- Testar login, assets, cookies, embeds e WebSocket/long polling se existirem.
- Se houver problema com cookies ou headers, preferir uma pagina Vercel com iframe/embed publico em vez de proxy total.

### Exemplo de pagina leve com iframe

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Metabase Hospital</title>
    <style>
      html,
      body,
      iframe {
        width: 100%;
        height: 100%;
        margin: 0;
        border: 0;
      }
    </style>
  </head>
  <body>
    <iframe
      src="https://SEU-METABASE-EXTERNO.com/public/dashboard/SEU_DASHBOARD"
      title="Metabase Hospital"
      loading="eager"
    ></iframe>
  </body>
</html>
```

Essa opcao costuma ser mais previsivel para dashboard publico do que tentar proxyar o Metabase inteiro.

## Medidas de estabilizacao se insistir em rodar Metabase dentro da Vercel

Estas medidas podem reduzir falhas, mas nao eliminam o risco estrutural:

1. Usar banco interno externo:

```env
MB_DB_TYPE=mysql
MB_DB_HOST=...
MB_DB_PORT=3306
MB_DB_DBNAME=...
MB_DB_USER=...
MB_DB_PASS=...
```

2. Desativar conteudo exemplo:

```env
MB_LOAD_SAMPLE_CONTENT=false
```

3. Definir heap:

```env
JAVA_OPTS=-Xmx512m
```

Em runtime limitado, `-Xmx768m` pode ser alto demais se o processo total tiver pouco espaco. Em container com 1 GB, `768m` pode fazer sentido; em serverless, pode competir com o restante do processo.

4. Reduzir carga inicial:

- nao gerar CSVs durante build/deploy;
- nao carregar dados durante startup do Metabase;
- nao usar H2 local;
- nao usar `latest`;
- nao executar migracoes repetidamente sem necessidade.

5. Aceitar que ainda pode cair:

Mesmo com ajustes, a Vercel continua nao sendo o runtime natural do Metabase. Se a queda for por timeout, cold start ou processo persistente, nao ha correcao definitiva dentro da propria Vercel.

## Monitoramento minimo

Criar uma rotina simples de verificacao:

```powershell
Invoke-WebRequest -UseBasicParsing https://SEU-DOMINIO-VERCEL/ | Select-Object StatusCode
```

Para Metabase externo:

```powershell
Invoke-WebRequest -UseBasicParsing https://SEU-METABASE-EXTERNO/api/health | Select-Object StatusCode
```

Se a URL da Vercel cair mas a URL externa estiver ok, o problema esta na camada Vercel/proxy.

Se as duas cairem, o problema esta no runtime do Metabase ou banco.

## Checklist de acao

- [ ] Confirmar se a Vercel roda Metabase ou apenas aponta para ele.
- [ ] Encontrar o projeto real no painel da Vercel.
- [ ] Baixar/exportar ou versionar `vercel.json` se existir.
- [ ] Confirmar logs de runtime da queda.
- [ ] Confirmar se existe banco interno `MetabaseDB` externo.
- [ ] Confirmar se nao esta usando H2.
- [ ] Fixar versao do Metabase.
- [ ] Separar carga de CSV da inicializacao do Metabase.
- [ ] Se houver host externo, usar Vercel como iframe/proxy leve.
- [ ] Se nao houver host externo, avaliar migrar apenas o runtime Metabase para container e manter dominio na Vercel.

## Informacoes que faltam para fechar o diagnostico

Para uma correcao objetiva, precisamos de pelo menos um destes conjuntos:

- URL atual da Vercel e log do erro quando cai;
- print ou texto do ultimo erro em **Deployments > Logs**;
- configuracao do projeto Vercel: root directory, build command e framework;
- qualquer `vercel.json` ou codigo que esteja no deploy real, caso nao seja este repositorio;
- confirmacao de onde ficam `MetabaseDB` e `HospitalDB`.

## Conclusao operacional

Da para manter a Vercel como a porta de entrada do projeto. O que nao e recomendado e manter o processo Metabase rodando diretamente nela.

Para reduzir quedas mantendo a URL da Vercel:

1. manter Vercel como frontend/proxy/embed;
2. rodar Metabase em ambiente persistente;
3. usar banco interno externo;
4. versionar a configuracao real da Vercel no repositorio;
5. monitorar separadamente Vercel, Metabase e banco.
