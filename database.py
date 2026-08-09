import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


if __name__ == "__main__":
    try:
        conexao = conectar()
        print("✅ Conectado ao PostgreSQL com sucesso!")
        conexao.close()
    except Exception as erro:
        print("❌ Erro ao conectar:")
        print(erro)