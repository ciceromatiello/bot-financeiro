from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# 💾 memória temporária (em produção use banco de dados)
gastos = []

@app.route("/", methods=["GET"])
def home():
    return "Bot Financeiro online 💰"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    print("🔥 CHEGOU NO WHATSAPP")

    resp = MessagingResponse()
    msg = resp.message()

    incoming_msg = request.values.get("Body", "").lower().strip()

    global gastos

    # 🟢 MENU
    if incoming_msg in ["oi", "olá", "menu", "ajuda", "help"]:
        msg.body(
            "👋 Bot Financeiro 💰\n\n"
            "📌 Comandos:\n"
            "━━━━━━━━━━━━━━\n"
            "💸 gastei 30,50 lanche\n"
            "📊 saldo\n"
            "📋 lista\n"
            "🗑️ apagar tudo\n"
            "━━━━━━━━━━━━━━\n"
        )
        return str(resp)

    # 💸 REGISTRAR GASTO
    if incoming_msg.startswith("gastei"):
        try:
            partes = incoming_msg.replace(",", ".").split()

            if len(partes) < 2:
                msg.body("❌ Use: gastei 30,50 lanche")
                return str(resp)

            valor = float(partes[1])
            categoria = " ".join(partes[2:]) if len(partes) > 2 else "geral"

            gastos.append({
                "valor": valor,
                "categoria": categoria
            })

            msg.body(f"✔️ Gasto registrado: R${valor:.2f} em {categoria}")

        except Exception as e:
            print("Erro:", e)
            msg.body("❌ Erro ao registrar. Use: gastei 30,50 lanche")

        return str(resp)

    # 📊 SALDO TOTAL
    if incoming_msg == "saldo":
        total = sum(g["valor"] for g in gastos)
        msg.body(f"💰 Total gasto: R${total:.2f}")
        return str(resp)

    # 📋 LISTAR GASTOS
    if incoming_msg in ["lista", "gastos"]:
        if not gastos:
            msg.body("📭 Nenhum gasto registrado ainda.")
        else:
            texto = "📋 Seus gastos:\n\n"
            for g in gastos:
                texto += f"• R${g['valor']:.2f} em {g['categoria']}\n"
            msg.body(texto)

        return str(resp)

    # 🗑️ APAGAR TUDO
    if incoming_msg == "apagar tudo":
        gastos.clear()
        msg.body("🗑️ Todos os gastos foram apagados!")
        return str(resp)

    # ❌ PADRÃO
    msg.body("❓ Não entendi 🤖\nDigite 'menu' para ver comandos.")
    return str(resp)


# 🚀 RENDER / PRODUÇÃO
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)