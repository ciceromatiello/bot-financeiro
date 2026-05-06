from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# 💾 memória temporária (depois pode virar banco de dados)
gastos = []

@app.route("/", methods=["GET"])
def home():
    return "Bot Financeiro online 💰"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():

    print("📩 Nova mensagem recebida")

    resp = MessagingResponse()
    msg = resp.message()

    # 🔥 IMPORTANTE: Twilio envia via FORM
    original_msg = request.form.get("Body", "")
    incoming_msg = original_msg.lower().strip()

    print("Mensagem:", incoming_msg)

    global gastos

    # 🟢 MENU
    if incoming_msg in ["oi", "olá", "ola", "menu", "ajuda", "help"]:
        msg.body(
            "👋 *Bot Financeiro* 💰\n\n"
            "📌 *Comandos disponíveis:*\n"
            "━━━━━━━━━━━━━━\n"
            "💸 Registrar gasto:\n"
            "   gastei 30,50 lanche\n\n"
            "📊 Ver saldo total:\n"
            "   saldo\n\n"
            "📋 Listar gastos:\n"
            "   lista\n\n"
            "🗑️ Apagar tudo:\n"
            "   apagar tudo\n"
            "━━━━━━━━━━━━━━\n\n"
            "💡 Exemplo:\n"
            "gastei 55,76 mercado"
        )
        return str(resp)

    # 💰 REGISTRAR GASTO
    elif "gastei" in incoming_msg:
        try:
            partes = incoming_msg.split()

            if len(partes) < 2:
                msg.body("❌ Use: gastei 30,50 lanche")
                return str(resp)

            # 🔥 suporta vírgula ou ponto
            valor_str = partes[1].replace(",", ".")
            valor = float(valor_str)

            categoria = " ".join(partes[2:]) if len(partes) > 2 else "geral"

            gastos.append({
                "valor": valor,
                "categoria": categoria
            })

            msg.body(f"✔️ Gasto registrado: R${valor:.2f} em {categoria}")

        except Exception as e:
            print("Erro:", e)
            msg.body("❌ Erro ao registrar. Use: gastei 30,50 lanche")

    # 📊 SALDO
    elif "saldo" in incoming_msg:
        total = sum(g["valor"] for g in gastos)
        msg.body(f"💰 Total gasto: R${total:.2f}")

    # 📋 LISTA
    elif "lista" in incoming_msg:
        if not gastos:
            msg.body("📭 Nenhum gasto registrado ainda.")
        else:
            texto = "📋 Seus gastos:\n\n"
            for g in gastos:
                texto += f"• R${g['valor']:.2f} em {g['categoria']}\n"
            msg.body(texto)

    # 🗑️ APAGAR TUDO
    elif "apagar tudo" in incoming_msg:
        gastos.clear()
        msg.body("🗑️ Todos os gastos foram apagados!")

    # ❌ PADRÃO
    else:
        msg.body("❓ Não entendi 🤖\nDigite *menu* para ver os comandos.")

    return str(resp)


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)