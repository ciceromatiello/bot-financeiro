from database import conectar


def criar_usuario(telefone):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios (telefone)
        VALUES (%s)
        ON CONFLICT (telefone) DO NOTHING
        RETURNING id;
        """,
        (telefone,)
    )

    resultado = cursor.fetchone()

    if resultado:
        usuario_id = resultado[0]
    else:
        cursor.execute(
            "SELECT id FROM usuarios WHERE telefone = %s;",
            (telefone,)
        )
        usuario_id = cursor.fetchone()[0]

    conexao.commit()

    cursor.close()
    conexao.close()

    return usuario_id


def definir_limite(telefone, limite):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE usuarios
        SET limite_mensal = %s
        WHERE id = %s;
        """,
        (limite, usuario_id)
    )

    conexao.commit()

    cursor.close()
    conexao.close()


def registrar_gasto(telefone, valor, descricao, categoria=None):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO gastos
        (usuario_id, valor, descricao, categoria)
        VALUES (%s, %s, %s, %s);
        """,
        (usuario_id, valor, descricao, categoria)
    )

    conexao.commit()

    cursor.close()
    conexao.close()


def obter_saldo(telefone):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT limite_mensal
        FROM usuarios
        WHERE id = %s;
        """,
        (usuario_id,)
    )

    limite = cursor.fetchone()[0] or 0

    cursor.execute(
        """
        SELECT COALESCE(SUM(valor), 0)
        FROM gastos
        WHERE usuario_id = %s
        AND DATE_TRUNC('month', data_gasto)
            = DATE_TRUNC('month', CURRENT_DATE);
        """,
        (usuario_id,)
    )

    total_gasto = cursor.fetchone()[0] or 0

    disponivel = limite - total_gasto

    cursor.close()
    conexao.close()

    return limite, total_gasto, disponivel


def listar_gastos(telefone):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, valor, descricao, data_gasto
        FROM gastos
        WHERE usuario_id = %s
        AND DATE_TRUNC('month', data_gasto)
            = DATE_TRUNC('month', CURRENT_DATE)
        ORDER BY data_gasto DESC;
        """,
        (usuario_id,)
    )

    gastos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return gastos


def apagar_gasto(telefone, gasto_id):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM gastos
        WHERE id = %s
        AND usuario_id = %s
        RETURNING valor, descricao;
        """,
        (gasto_id, usuario_id)
    )

    resultado = cursor.fetchone()

    conexao.commit()

    cursor.close()
    conexao.close()

    return resultado


def apagar_todos_gastos(telefone):
    usuario_id = criar_usuario(telefone)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM gastos
        WHERE usuario_id = %s
        AND DATE_TRUNC('month', data_gasto)
            = DATE_TRUNC('month', CURRENT_DATE);
        """,
        (usuario_id,)
    )

    quantidade = cursor.rowcount

    conexao.commit()

    cursor.close()
    conexao.close()

    return quantidade