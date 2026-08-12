from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import os

app = Flask(__name__)


# ==========================================
# 🗄️ BANCO DE DADOS
# ==========================================

def conectar():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    return psycopg2.connect(database_url)


def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    # 👤 Usuários e limites
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            telefone VARCHAR(50) PRIMARY KEY,
            limite_mensal NUMERIC(12,2) DEFAULT 0
        )
    """)

    # 💸 Gastos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            telefone VARCHAR(50) NOT NULL,
            valor NUMERIC(12,2) NOT NULL,
            categoria VARCHAR(255) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def garantir_usuario(telefone):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO usuarios (telefone, limite_mensal)
        VALUES (%s, 0)
        ON CONFLICT (telefone) DO NOTHING
    """, (telefone,))

    conn.commit()
    cur.close()
    conn.close()


def obter_limite(telefone):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT limite_mensal
        FROM usuarios
        WHERE telefone = %s
    """, (telefone,))

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado:
        return float(resultado[0])

    return 0


def definir_limite(telefone, valor):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE usuarios
        SET limite_mensal = %s
        WHERE telefone = %s
    """, (valor, telefone))

    conn.commit()
    cur.close()
    conn.close()


def registrar_gasto(telefone, valor, categoria):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO gastos (telefone, valor, categoria)
        VALUES (%s, %s, %s)
    """, (telefone, valor, categoria))

    conn.commit()
    cur.close()
    conn.close()


def obter_gastos(telefone):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, valor, categoria
        FROM gastos
        WHERE telefone = %s
        ORDER BY id ASC
    """, (telefone,))

    resultados = cur.fetchall()

    cur.close()
    conn.close()

    return resultados


def obter_total(telefone):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM gastos
        WHERE telefone = %s
    """, (telefone,))

    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return float(total)


def apagar_gasto_por_posicao(telefone, posicao):
    gastos_usuario = obter_gastos(telefone)

    if posicao < 1 or posicao > len(gastos_usuario):
        return None

    gasto = gastos_usuario[posicao - 1]

    id_gasto = gasto[0]
    valor = float(gasto[1])
    categoria = gasto[2]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM gastos
        WHERE id = %s AND telefone = %s
    """, (id_gasto, telefone))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "valor": valor,
        "categoria": categoria
    }


def apagar_todos_gastos(telefone):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM gastos
        WHERE telefone = %s
    """, (telefone,))

    quantidade = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    return quantidade


# ==========================================
# 🌐 ROTAS
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return "Bot Financeiro online 💰"


@app.route("/whatsapp", methods=["POST"])
def whatsapp():

    print("📩 Nova mensagem recebida")

    resp = MessagingResponse()
    msg = resp.message()

    original_msg = request.form.get("Body", "")
    incoming_msg = original_msg.lower().strip()

    # 📱 Identifica quem enviou
    telefone = request.form.get("From", "desconhecido")

    print("Mensagem:", incoming_msg)
    print("Usuário:", telefone)

    try:
        garantir_usuario(telefone)

        # ==========================================
        # 🟢 MENU
        # ==========================================

        if incoming_msg in ["oi", "olá", "ola", "menu", "ajuda", "help"]:

            msg.body(
                "👋 *Bot Financeiro* 💰\n\n"
                "📌 *Comandos disponíveis:*\n"
                "━━━━━━━━━━━━━━━━━━\n\n"

                "💸 *Registrar gasto:*\n"
                "gastei 30,50 lanche\n\n"

                "📊 *Ver saldo:*\n"
                "saldo\n\n"

                "📋 *Listar gastos:*\n"
                "lista\n\n"

                "🎯 *Definir limite:*\n"
                "limite 2000\n\n"

                "🎯 *Ver limite:*\n"
                "limite\n\n"

                "🗑️ *Apagar um gasto:*\n"
                "apagar 3\n\n"

                "⚠️ *Apagar todos:*\n"
                "apagar tudo\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
                "💡 *Exemplo:*\n"
                "gastei 55,76 mercado"
            )

        # ==========================================
        # 🎯 DEFINIR LIMITE
        # ==========================================

        elif incoming_msg.startswith("limite "):

            try:
                partes = incoming_msg.split()

                if len(partes) != 2:
                    msg.body("❌ Use assim:\nlimite 2000")
                    return str(resp)

                valor = float(partes[1].replace(",", "."))

                if valor <= 0:
                    msg.body("❌ O limite precisa ser maior que zero.")
                    return str(resp)

                definir_limite(telefone, valor)

                total = obter_total(telefone)
                restante = valor - total

                msg.body(
                    f"🎯 *Limite definido!*\n\n"
                    f"💰 Limite: R${valor:.2f}\n"
                    f"📊 Total gasto: R${total:.2f}\n"
                    f"💵 Disponível: R${restante:.2f}"
                )

            except ValueError:
                msg.body(
                    "❌ Valor inválido.\n\n"
                    "Exemplo:\n"
                    "limite 2000"
                )

        # ==========================================
        # 🎯 VER LIMITE
        # ==========================================

        elif incoming_msg == "limite":

            limite = obter_limite(telefone)
            total = obter_total(telefone)

            if limite <= 0:

                msg.body(
                    "🎯 *Limite não definido.*\n\n"
                    "Para definir:\n"
                    "limite 2000"
                )

            else:

                restante = limite - total

                if restante >= 0:

                    msg.body(
                        f"🎯 *Seu limite*\n\n"
                        f"💰 Limite: R${limite:.2f}\n"
                        f"📊 Total gasto: R${total:.2f}\n"
                        f"🟢 Disponível: R${restante:.2f}"
                    )

                else:

                    msg.body(
                        f"🚨 *Limite ultrapassado!*\n\n"
                        f"🎯 Limite: R${limite:.2f}\n"
                        f"📊 Total gasto: R${total:.2f}\n"
                        f"🔴 Ultrapassou: R${abs(restante):.2f}"
                    )

        # ==========================================
        # 💸 REGISTRAR GASTO
        # ==========================================

        elif incoming_msg.startswith("gastei"):

            try:
                partes = incoming_msg.split()

                if len(partes) < 2:
                    msg.body(
                        "❌ Use assim:\n"
                        "gastei 30,50 lanche"
                    )
                    return str(resp)

                valor = float(partes[1].replace(",", "."))

                if valor <= 0:
                    msg.body("❌ O valor precisa ser maior que zero.")
                    return str(resp)

                categoria = (
                    " ".join(partes[2:])
                    if len(partes) > 2
                    else "geral"
                )

                registrar_gasto(
                    telefone,
                    valor,
                    categoria
                )

                total = obter_total(telefone)
                limite = obter_limite(telefone)

                resposta = (
                    f"✔️ *Gasto registrado!*\n\n"
                    f"💸 Valor: R${valor:.2f}\n"
                    f"📌 Categoria: {categoria}\n"
                    f"📊 Total gasto: R${total:.2f}"
                )

                if limite > 0:

                    restante = limite - total

                    resposta += (
                        f"\n\n🎯 Limite: R${limite:.2f}"
                    )

                    if restante > 0:

                        resposta += (
                            f"\n🟢 Disponível: R${restante:.2f}"
                        )

                    elif restante == 0:

                        resposta += (
                            "\n\n⚠️ *ATENÇÃO!*\n"
                            "Você atingiu seu limite de gastos!"
                        )

                    else:

                        resposta += (
                            "\n\n🚨 *ATENÇÃO!*\n"
                            f"Você ultrapassou seu limite em "
                            f"R${abs(restante):.2f}!"
                        )

                msg.body(resposta)

            except ValueError:

                msg.body(
                    "❌ Valor inválido.\n\n"
                    "Use:\n"
                    "gastei 30,50 lanche"
                )

        # ==========================================
        # 📊 SALDO
        # ==========================================

        elif incoming_msg == "saldo":

            total = obter_total(telefone)
            limite = obter_limite(telefone)

            if limite > 0:

                restante = limite - total

                if restante >= 0:

                    msg.body(
                        f"💰 *Saldo dos gastos*\n\n"
                        f"📊 Total gasto: R${total:.2f}\n"
                        f"🎯 Limite: R${limite:.2f}\n"
                        f"🟢 Disponível: R${restante:.2f}"
                    )

                else:

                    msg.body(
                        f"💰 *Saldo dos gastos*\n\n"
                        f"📊 Total gasto: R${total:.2f}\n"
                        f"🎯 Limite: R${limite:.2f}\n"
                        f"🔴 Ultrapassado: R${abs(restante):.2f}"
                    )

            else:

                msg.body(
                    f"💰 *Total gasto:* R${total:.2f}\n\n"
                    "🎯 Você ainda não definiu um limite."
                )

        # ==========================================
        # 📋 LISTA
        # ==========================================

        elif incoming_msg == "lista":

            gastos_usuario = obter_gastos(telefone)

            if not gastos_usuario:

                msg.body(
                    "📭 Nenhum gasto registrado ainda."
                )

            else:

                texto = "📋 *Seus gastos:*\n\n"

                total = 0

                for numero, gasto in enumerate(
                    gastos_usuario,
                    start=1
                ):

                    valor = float(gasto[1])
                    categoria = gasto[2]

                    total += valor

                    texto += (
                        f"*{numero}.* "
                        f"R${valor:.2f} — "
                        f"{categoria}\n"
                    )

                texto += (
                    f"\n💰 *Total:* R${total:.2f}\n\n"
                    "🗑️ Para apagar um gasto:\n"
                    "apagar 3"
                )

                msg.body(texto)

        # ==========================================
        # 🗑️ APAGAR TUDO
        # IMPORTANTE: fica antes de "apagar número"
        # ==========================================

        elif incoming_msg == "apagar tudo":

            quantidade = apagar_todos_gastos(telefone)

            if quantidade == 0:

                msg.body(
                    "📭 Não existem gastos para apagar."
                )

            else:

                msg.body(
                    "🗑️ *Todos os gastos foram apagados!*\n\n"
                    f"📊 {quantidade} gasto(s) removido(s)."
                )

        # ==========================================
        # 🗑️ APAGAR UM GASTO
        # ==========================================

        elif incoming_msg.startswith("apagar "):

            try:
                partes = incoming_msg.split()

                if len(partes) != 2:

                    msg.body(
                        "❌ Use assim:\n"
                        "apagar 3"
                    )

                    return str(resp)

                numero = int(partes[1])

                gasto_removido = apagar_gasto_por_posicao(
                    telefone,
                    numero
                )

                if gasto_removido is None:

                    msg.body(
                        f"❌ Gasto número {numero} "
                        "não encontrado.\n\n"
                        "Use *lista* para ver seus gastos."
                    )

                else:

                    total = obter_total(telefone)

                    msg.body(
                        f"🗑️ *Gasto apagado!*\n\n"
                        f"💸 Valor: "
                        f"R${gasto_removido['valor']:.2f}\n"
                        f"📌 Categoria: "
                        f"{gasto_removido['categoria']}\n\n"
                        f"💰 Total agora: R${total:.2f}"
                    )

            except ValueError:

                msg.body(
                    "❌ Número inválido.\n\n"
                    "Exemplo:\n"
                    "apagar 3"
                )

        # ==========================================
        # ❓ COMANDO NÃO RECONHECIDO
        # ==========================================

        else:

            msg.body(
                "❓ Não entendi 🤖\n\n"
                "Digite *menu* para ver os comandos."
            )

    except Exception as e:

        print("❌ ERRO:", e)

        msg.body(
            "⚠️ Ocorreu um erro no Bot Financeiro.\n"
            "Tente novamente em alguns instantes."
        )

    return str(resp)


# ==========================================
# 🚀 INICIALIZAÇÃO
# ==========================================

criar_tabelas()

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )