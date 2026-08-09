from comandos import processar_mensagem


telefone = "551234567890"

print(processar_mensagem(telefone, "limite 2000"))

print()

print(
    processar_mensagem(
        telefone,
        "gastei 50,90 mercado"
    )
)

print()

print(processar_mensagem(telefone, "saldo"))