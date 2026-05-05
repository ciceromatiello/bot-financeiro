from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# 💾 memória simples (depois podemos trocar por banco)
gastos = []

@app.route("/", methods=["GET"])
def home():
    return "Bot financeiro online!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower().strip()
    resp = MessagingResponse()
    msg = resp.message()

    global gastos

    # 💬 oi
    if "oi" in incoming_msg:
        msg.body("Olá 👋! Pode registrar: gastei 30 lanche")

    # 💰 registrar gasto
    elif "gastei" in incoming_msg:
        try:
            partes = incoming_msg.split()
            valor = float(partes[1])
            categoria = " ".join(partes[2:]) if len(partes) > 2 else "geral"

            gastos.append({"valor": valor, "categoria": categoria})

            msg.body(f"✔ Gasto registrado: R${valor} em {categoria}")
        except:
            msg.body("Formato correto: gastei 30 lanche")

    # 📊 saldo
    elif "saldo" in incoming_msg:
        total = sum(g["valor"] for g in gastos)
        msg.body(f"💰 Seu total gasto é R${total:.2f}")

    # 📋 lista
    elif "lista" in incoming_msg or "gastos" in incoming_msg:
        if not gastos:
            msg.body("Nenhum gasto registrado ainda.")
        else:
            texto = "📋 Seus gastos:\n"
            for g in gastos:
                texto += f"- R${g['valor']} em {g['categoria']}\n"
            msg.body(texto)

    else:
        msg.body("Não entendi 🤖. Use: oi, gastei, saldo, lista")

    return str(resp)