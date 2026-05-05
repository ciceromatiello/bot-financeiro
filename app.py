from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# 🏠 Rota de teste (Render + navegador)
@app.route("/", methods=["GET"])
def home():
    return "Bot financeiro está online!"

# 💬 Webhook do WhatsApp (Twilio)
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # Mensagem recebida
    incoming_msg = request.values.get("Body", "").lower()

    # Resposta do bot
    resp = MessagingResponse()
    msg = resp.message()

    # Lógica simples do bot financeiro (exemplo)
    if "oi" in incoming_msg:
        msg.body("Olá! 👋 Sou seu bot financeiro.")
    elif "gastei" in incoming_msg:
        msg.body("Anotado! 💰 Seu gasto foi registrado (versão base).")
    elif "saldo" in incoming_msg:
        msg.body("Seu saldo ainda não está implementado 🙂")
    else:
        msg.body("Não entendi 🤖. Tente: oi, gastei, saldo")

    return str(resp)


# 🚀 IMPORTANTE: compatível com Render (porta dinâmica)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)