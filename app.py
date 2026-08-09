from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# 💾 Memória temporária
gastos = []

# 🎯 Limite de gastos
limite_gastos = 0


@app.route("/", methods=["GET"])
def home():
    return "Bot Financeiro online 💰"


@app.route("/whatsapp", methods=["POST"])
def whatsapp():

    print("📩 Nova mensagem recebida")

    resp = MessagingResponse()
    msg = resp.message()

    # 📱 Mensagem recebida pelo WhatsApp
    original_msg = request.form.get("Body", "")
    incoming_msg = original_msg.lower().strip()

    print("Mensagem:", incoming_msg)

    global gastos
    global limite_gastos

    # 🟢 MENU
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
            "limite 500\n\n"

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

        return str(resp)

    # 🎯 DEFINIR LIMITE
    elif incoming_msg.startswith("limite "):

        try:
            partes = incoming_msg.split()

            if len(partes) != 2:
                msg.body("❌ Use assim:\nlimite 500")
                return str(resp)

            valor_str = partes[1].replace(",", ".")
            novo_limite = float(valor_str)

            if novo_limite <= 0:
                msg.body("❌ O limite precisa ser maior que zero.")
                return str(resp)

            limite_gastos = novo_limite

            total = sum(g["valor"] for g in gastos)
            restante = limite_gastos - total

            msg.body(
                f"🎯 *Limite definido!*\n\n"
                f"💰 Limite: R${limite_gastos:.2f}\n"
                f"📊 Já gasto: R${total:.2f}\n"
                f"💵 Disponível: R${restante:.2f}"
            )

        except Exception as e:
            print("Erro:", e)
            msg.body("❌ Valor inválido.\nUse: limite 500")

    # 🎯 VER LIMITE
    elif incoming_msg == "limite":

        total = sum(g["valor"] for g in gastos)

        if limite_gastos <= 0:
            msg.body(
                "🎯 *Limite não definido.*\n\n"
                "Para definir, use:\n"
                "limite 500"
            )
        else:

            restante = limite_gastos - total

            if restante > 0:
                msg.body(
                    f"🎯 *Seu limite*\n\n"
                    f"💰 Limite: R${limite_gastos:.2f}\n"
                    f"📊 Gasto: R${total:.2f}\n"
                    f"🟢 Disponível: R${restante:.2f}"
                )

            elif restante == 0:
                msg.body(
                    f"⚠️ *LIMITE ATINGIDO!*\n\n"
                    f"🎯 Limite: R${limite_gastos:.2f}\n"
                    f"📊 Gasto: R${total:.2f}\n"
                    f"🔴 Disponível: R$0,00"
                )

            else:
                ultrapassado = abs(restante)

                msg.body(
                    f"🚨 *LIMITE ULTRAPASSADO!*\n\n"
                    f"🎯 Limite: R${limite_gastos:.2f}\n"
                    f"📊 Gasto: R${total:.2f}\n"
                    f"🔴 Ultrapassou: R${ultrapassado:.2f}"
                )

    # 💰 REGISTRAR GASTO
    elif incoming_msg.startswith("gastei"):

        try:
            partes = incoming_msg.split()

            if len(partes) < 2:
                msg.body("❌ Use:\ngastei 30,50 lanche")
                return str(resp)

            # Suporta vírgula ou ponto
            valor_str = partes[1].replace(",", ".")
            valor = float(valor_str)

            if valor <= 0:
                msg.body("❌ O valor precisa ser maior que zero.")
                return str(resp)

            categoria = (
                " ".join(partes[2:])
                if len(partes) > 2
                else "geral"
            )

            gastos.append({
                "valor": valor,
                "categoria": categoria
            })

            total = sum(g["valor"] for g in gastos)

            resposta = (
                f"✔️ *Gasto registrado!*\n\n"
                f"💸 Valor: R${valor:.2f}\n"
                f"📌 Categoria: {categoria}\n"
                f"📊 Total gasto: R${total:.2f}"
            )

            # ⚠️ AVISAR SOBRE LIMITE
            if limite_gastos > 0:

                restante = limite_gastos - total

                if restante > 0:
                    resposta += (
                        f"\n\n🎯 Limite: R${limite_gastos:.2f}"
                        f"\n🟢 Disponível: R${restante:.2f}"
                    )

                elif restante == 0:
                    resposta += (
                        "\n\n⚠️ *ATENÇÃO!*\n"
                        "Você atingiu seu limite de gastos!"
                    )

                else:
                    ultrapassado = abs(restante)

                    resposta += (
                        "\n\n🚨 *ATENÇÃO!*\n"
                        f"Você ultrapassou seu limite em "
                        f"R${ultrapassado:.2f}!"
                    )

            msg.body(resposta)

        except Exception as e:
            print("Erro:", e)
            msg.body(
                "❌ Erro ao registrar.\n"
                "Use: gastei 30,50 lanche"
            )

    # 📊 SALDO
    elif incoming_msg == "saldo":

        total = sum(g["valor"] for g in gastos)

        if limite_gastos > 0:

            restante = limite_gastos - total

            if restante >= 0:
                msg.body(
                    f"💰 *Saldo dos gastos*\n\n"
                    f"📊 Total gasto: R${total:.2f}\n"
                    f"🎯 Limite: R${limite_gastos:.2f}\n"
                    f"🟢 Disponível: R${restante:.2f}"
                )
            else:
                msg.body(
                    f"💰 *Saldo dos gastos*\n\n"
                    f"📊 Total gasto: R${total:.2f}\n"
                    f"🎯 Limite: R${limite_gastos:.2f}\n"
                    f"🔴 Ultrapassado: R${abs(restante):.2f}"
                )

        else:
            msg.body(
                f"💰 *Total gasto:* R${total:.2f}"
            )

    # 📋 LISTAR GASTOS
    elif incoming_msg == "lista":

        if not gastos:
            msg.body("📭 Nenhum gasto registrado ainda.")

        else:

            texto = "📋 *Seus gastos:*\n\n"

            for i, g in enumerate(gastos, start=1):

                texto += (
                    f"*{i}.* R${g['valor']:.2f} "
                    f"— {g['categoria']}\n"
                )

            total = sum(g["valor"] for g in gastos)

            texto += (
                f"\n💰 *Total:* R${total:.2f}\n\n"
                "🗑️ Para apagar um gasto:\n"
                "apagar 3"
            )

            msg.body(texto)

    # 🗑️ APAGAR UM GASTO
    elif incoming_msg.startswith("apagar ") and incoming_msg != "apagar tudo":

        try:

            partes = incoming_msg.split()

            if len(partes) != 2:
                msg.body(
                    "❌ Use assim:\n"
                    "apagar 3"
                )
                return str(resp)

            numero = int(partes[1])

            if numero < 1 or numero > len(gastos):
                msg.body(
                    f"❌ Gasto número {numero} não encontrado.\n\n"
                    "Use *lista* para ver os números dos gastos."
                )
                return str(resp)

            gasto_removido = gastos.pop(numero - 1)

            msg.body(
                f"🗑️ *Gasto apagado!*\n\n"
                f"💸 Valor: R${gasto_removido['valor']:.2f}\n"
                f"📌 Categoria: {gasto_removido['categoria']}"
            )

        except ValueError:

            msg.body(
                "❌ Número inválido.\n\n"
                "Exemplo:\n"
                "apagar 3"
            )

    # 🗑️ APAGAR TUDO
    elif incoming_msg == "apagar tudo":

        if not gastos:
            msg.body("📭 Não existem gastos para apagar.")

        else:
            quantidade = len(gastos)

            gastos.clear()

            msg.body(
                f"🗑️ *Todos os gastos foram apagados!*\n\n"
                f"📊 {quantidade} gasto(s) removido(s)."
            )

    # ❌ PADRÃO
    else:

        msg.body(
            "❓ Não entendi 🤖\n\n"
            "Digite *menu* para ver os comandos."
        )

    return str(resp)


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)