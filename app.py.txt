from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import os

app = Flask(__name__)

conn = psycopg2.connect(os.environ["DATABASE_URL"])

def get_user(phone):
    cur = conn.cursor()
    cur.execute("SELECT id, limite FROM users WHERE phone=%s", (phone,))
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users (phone) VALUES (%s) RETURNING id", (phone,))
        conn.commit()
        return cur.fetchone()[0], 0

    return user

@app.route("/bot", methods=["POST"])
def bot():
    phone = request.values.get("From")
    msg = request.values.get("Body", "").lower()

    user_id, limite = get_user(phone)
    cur = conn.cursor()

    resp = MessagingResponse()

    if msg.startswith("limite"):
        try:
            valor = float(msg.split()[1])
            cur.execute("UPDATE users SET limite=%s WHERE id=%s", (valor, user_id))
            conn.commit()
            resp.message(f"✅ Limite: R${valor}")
        except:
            resp.message("Use: limite 500")

    elif msg == "total":
        cur.execute("SELECT SUM(valor) FROM expenses WHERE user_id=%s", (user_id,))
        total = cur.fetchone()[0] or 0
        resp.message(f"💰 Total: R${total}")

    else:
        try:
            partes = msg.split()
            valor = float(partes[0])
            desc = " ".join(partes[1:])

            cur.execute(
                "INSERT INTO expenses (user_id, valor, descricao) VALUES (%s, %s, %s)",
                (user_id, valor, desc)
            )
            conn.commit()

            cur.execute("SELECT SUM(valor) FROM expenses WHERE user_id=%s", (user_id,))
            total = cur.fetchone()[0]

            resposta = f"🧾 {desc}: R${valor}\n💰 Total: R${total}"

            if limite:
                if total >= limite:
                    resposta += "\n🚨 Limite atingido!"
                elif total >= limite * 0.8:
                    resposta += "\n⚠️ 80% do limite!"

            resp.message(resposta)

        except:
            resp.message("Use: 50 mercado | limite 500 | total")

    return str(resp)