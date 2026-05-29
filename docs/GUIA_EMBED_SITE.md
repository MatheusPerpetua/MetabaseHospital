# Guia para rodar Metabase e embedar no site

## Arquitetura recomendada

O caminho mais estavel para este projeto e separar o BI do site:

```text
Usuario
  -> Site / portfolio / app web
     -> Embed do dashboard
        -> Metabase em Railway, Render, Fly.io, VPS, Cloud Run ou Metabase Cloud
           -> HospitalDB com os dados analiticos
           -> MetabaseDB com configuracoes internas do Metabase
```

O site pode ficar na Vercel. O Metabase deve ficar em um ambiente com processo persistente, porque ele e uma aplicacao Java/JVM e precisa continuar rodando como servico web.

## Escolha do tipo de embed

### 1. Public embed

Use quando o dashboard pode ser visto por qualquer pessoa que tenha o link.

Vantagens:

- implementacao mais simples;
- funciona com `iframe`;
- bom para portfolio, demonstracao publica e BI aberto.

Limites:

- qualquer pessoa com a URL publica consegue abrir o dashboard;
- filtros na URL podem ser alterados pelo visitante;
- nao e ideal para dados privados ou por usuario.

Fluxo:

1. No Metabase, publique o dashboard.
2. Abra o menu de compartilhamento.
3. Escolha a opcao de embed/public iframe.
4. Cole o `iframe` no seu site.

Exemplo:

```html
<iframe
  src="https://seu-metabase.up.railway.app/public/dashboard/UUID_DO_DASHBOARD#bordered=false&titled=false"
  width="100%"
  height="900"
  frameborder="0"
  allowtransparency="true"
></iframe>
```

### 2. Guest embed com JWT

Use quando o dashboard fica dentro do seu site, mas voce quer controlar o acesso pelo backend do proprio site.

Vantagens:

- o visitante nao precisa ter conta no Metabase;
- o embed so carrega com um JWT assinado;
- da para aplicar parametros travados, por exemplo hospital, cliente ou unidade;
- a chave secreta fica no servidor do site, nao no navegador.

Limites:

- exige uma rota backend no site para gerar o token;
- nao substitui recursos avancados de SSO;
- row/column security, drill-through completo e analiticos por usuario exigem recursos mais avancados.

Fluxo:

1. No Metabase, ative `Admin > Embedding`.
2. Publique o dashboard como guest embed.
3. Copie o snippet gerado pelo proprio Metabase.
4. No site, crie uma rota server-side para gerar o JWT.
5. Guarde a chave em variavel de ambiente do site.

Exemplo de variaveis do site:

```env
METABASE_SITE_URL=https://seu-metabase.up.railway.app
METABASE_EMBEDDING_SECRET_KEY=sua_chave_de_embedding
METABASE_DASHBOARD_ID=1
```

Exemplo de rota server-side em Next.js:

```ts
import jwt from "jsonwebtoken";

export async function POST(request: Request) {
  const { entityType, entityId } = await request.json();

  const dashboardId = Number(process.env.METABASE_DASHBOARD_ID);
  const secret = process.env.METABASE_EMBEDDING_SECRET_KEY;

  if (!secret || entityType !== "dashboard" || Number(entityId) !== dashboardId) {
    return Response.json({ error: "Forbidden" }, { status: 403 });
  }

  const payload = {
    resource: { dashboard: dashboardId },
    params: {},
    exp: Math.round(Date.now() / 1000) + 10 * 60,
  };

  return Response.json({ jwt: jwt.sign(payload, secret) });
}
```

Observacao: este exemplo e propositalmente simples. Em uma area logada, valide a sessao do usuario antes de emitir o JWT e preencha `params` com filtros travados.

## Configuracao no Metabase

No servico do Metabase, mantenha estas variaveis principais:

```env
PORT=3000
MB_JETTY_PORT=3000
MB_JETTY_HOST=0.0.0.0
MB_SITE_NAME=Metabase Hospital
MB_SITE_URL=https://seu-metabase.up.railway.app
MB_LOAD_SAMPLE_CONTENT=false
JAVA_OPTS=-Xmx768m

MB_DB_TYPE=mysql
MB_DB_HOST=...
MB_DB_PORT=...
MB_DB_DBNAME=...
MB_DB_USER=...
MB_DB_PASS=...
```

Se quiser controlar a chave de embed por ambiente, configure tambem:

```env
MB_EMBEDDING_SECRET_KEY=sua_chave_de_embedding
```

## Ordem pratica de implantacao

1. Subir `HospitalDB` no Railway.
2. Subir `MetabaseDB` separado no Railway.
3. Subir o servico Metabase usando o `Dockerfile`.
4. Rodar `python src/Geradorbase.py`.
5. Rodar `python src/inserirbanco.py` apontando para o `HospitalDB`.
6. Conectar o Metabase no `HospitalDB`.
7. Criar perguntas e dashboards.
8. Publicar o dashboard como public embed ou guest embed.
9. Inserir o embed no site.

## Referencias oficiais

- Public sharing e public embeds: https://www.metabase.com/docs/latest/embedding/public-links
- Guest embeds: https://www.metabase.com/docs/latest/embedding/guest-embedding
- Static/signed embedding: https://www.metabase.com/docs/latest/embedding/static-embedding
- Variaveis de ambiente do Metabase: https://www.metabase.com/docs/latest/configuring-metabase/environment-variables
