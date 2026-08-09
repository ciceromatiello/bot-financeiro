from financeiro import (
    definir_limite,
    registrar_gasto,
    obter_saldo
)

telefone = "551234567890"

definir_limite(telefone, 2000)

registrar_gasto(
    telefone,
    35.90,
    "Mercado",
    "Alimentação"
)

limite, gasto, disponivel = obter_saldo(telefone)

print()
print("===== RESUMO FINANCEIRO =====")
print(f"Limite: R$ {limite:.2f}")
print(f"Gasto: R$ {gasto:.2f}")
print(f"Disponível: R$ {disponivel:.2f}")