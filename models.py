from database import conectar


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            telefone VARCHAR(30) UNIQUE NOT NULL,
            limite_mensal NUMERIC(10, 2) DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            valor NUMERIC(10, 2) NOT NULL,
            descricao TEXT NOT NULL,
            categoria VARCHAR(100),
            data_gasto TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conexao.commit()

    cursor.close()
    conexao.close()

    print("✅ Tabelas criadas com sucesso!")


if __name__ == "__main__":
    criar_tabelas()