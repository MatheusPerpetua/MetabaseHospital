from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Carregar variáveis de ambiente
load_dotenv()


def _get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(
        "Variavel de ambiente ausente: "
        + " ou ".join(names)
        + ". Confira seu arquivo .env."
    )


def _get_port(*names):
    raw_port = _get_env(*names)
    try:
        return int(raw_port)
    except ValueError as exc:
        raise RuntimeError(
            "A variavel "
            + " ou ".join(names)
            + " precisa ser um numero inteiro."
        ) from exc


HOST = _get_env("MYSQLHOST", "DB_HOST", "HOST")
DATABASE = _get_env("MYSQLDATABASE", "DB_NAME", "DATABASE")
USER_DB = _get_env("MYSQLUSER", "DB_USER", "USER_DB")
PASSWORD_DB = _get_env("MYSQLPASSWORD", "DB_PASSWORD", "PASSWORD_DB", "PASSWORDDB")
PORT = _get_port("MYSQLPORT", "DB_PORT", "PORT", "PORTA")

# Configuração de SQLAlchemy para o ambiente de produção
ENGINEH = create_engine(
    URL.create(
        "mysql+pymysql",
        username=USER_DB,
        password=PASSWORD_DB,
        host=HOST,
        port=PORT,
        database=DATABASE,
    ),
    pool_pre_ping=True,
)
