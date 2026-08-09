import re

from financeiro import (
    definir_limite,
    registrar_gasto,
    obter_saldo,
    listar_gastos,
    apagar_gasto,
    apagar_todos_gastos
)


# Guarda quem está aguardando confirmação para apagar tudo
confirmacoes_apagar = set()


def processar_mensagem(telefone, mensagem):
    mensagem = mensagem.strip().lower()

    # =========================
    # CANCELAR
    # =========================
    if mensagem == "cancelar":
        confirmacoes_apagar.discard(telefone)

        return (
            "❌ Operação cancelada.\n\n"
            "Nenhum gasto foi apagado."
        )

    # =========================
    # CONFIRMAR APAGAR TUDO
    # =========================
    if mensagem in ["confirmar", "sim"] and telefone in confirmacoes_apagar:

        confirmacoes_apagar.discard(telefone)

        quantidade = apagar_todos_gastos(telefone)

        if quantidade == 0:
            return "ℹ️ Você não possui gastos neste mês."

        return (
            "🗑️ GASTOS APAGADOS!\n\n"
            f"✅ {quantidade} gasto(s) foram removidos."
        )

    # =========================
    # APAGAR TUDO
    # =========================
    if mensagem == "apagar tudo":

        confirmacoes_apagar.add(telefone)

        return (
            "⚠️ ATENÇÃO!\n\n"
            "Você está prestes a apagar TODOS os gastos "
            "registrados neste mês.\n\n"
            "Essa ação não poderá ser desfeita.\n\n"
            "Digite *CONFIRMAR* para continuar.\n"
            "Digite *CANCELAR* para desistir."
        )

    # =========================
    # LISTAR GASTOS
    # =========================
    if mensagem in ["gastos", "listar gastos", "meus gastos", "historico"]:

        gastos = listar_gastos(telefone)

        if not gastos:
            return (
                "📋 SEUS GASTOS\n\n"
                "Você ainda não possui gastos registrados neste mês."
            )

        resposta = "📋 SEUS GASTOS DO MÊS\n\n"

        for numero, gasto in enumerate(gastos, start=1):
            gasto_id, valor, descricao, data = gasto

            resposta += (
                f"{numero}️⃣ R$ {float(valor):.2f} - {descricao}\n"
            )

        resposta += (
            "\n🗑️ Para apagar um gasto:\n"
            "Digite *apagar número*\n\n"
            "Exemplo: *apagar 2*\n\n"
            "⚠️ Para apagar todos:\n"
            "*apagar tudo*"
        )

        return resposta

    # =========================
    # APAGAR GASTO ESCOLHIDO
    # =========================
    if mensagem.startswith("apagar "):

        partes = mensagem.split()

        if len(partes) != 2:
            return (
                "❌ Comando inválido.\n\n"
                "Use assim:\n"
                "*apagar 2*"
            )

        try:
            numero = int(partes[1])
        except ValueError:
            return (
                "❌ Informe o número do gasto.\n\n"
                "Exemplo:\n"
                "*apagar 2*"
            )

        if numero <= 0:
            return "❌ Escolha um número válido."

        gastos = listar_gastos(telefone)

        if not gastos:
            return "ℹ️ Você não possui gastos neste mês."

        if numero > len(gastos):
            return (
                f"❌ Não existe o gasto número {numero}.\n\n"
                f"Você possui {len(gastos)} gasto(s) listado(s).\n\n"
                "Digite *gastos* para consultar."
            )

        gasto_id, valor, descricao, data = gastos[numero - 1]

        resultado = apagar_gasto(telefone, gasto_id)

        if not resultado:
            return (
                "❌ Não foi possível apagar esse gasto."
            )

        return (
            "🗑️ GASTO APAGADO!\n\n"
            f"💰 Valor: R$ {float(valor):.2f}\n"
            f"📝 Descrição: {descricao}\n\n"
            "✅ O gasto foi removido com sucesso."
        )

    # =========================
    # LIMPAR
    # =========================
    if mensagem == "limpar":

        confirmacoes_apagar.discard(telefone)

        return (
            "🧹 CONVERSA ORGANIZADA!\n\n"
            "O bot limpou as operações pendentes.\n\n"
            "⚠️ O Twilio/WhatsApp não permite que o bot "
            "apague as mensagens antigas da conversa.\n\n"
            "Se quiser começar novamente, digite *menu*."
        )

    # =========================
    # DEFINIR LIMITE
    # =========================
    if mensagem.startswith("limite"):

        partes = mensagem.split()

        if len(partes) < 2:
            return "❌ Informe o valor. Exemplo: limite 2000"

        valor_texto = partes[1].replace(",", ".")

        try:
            limite = float(valor_texto)
        except ValueError:
            return "❌ Valor inválido. Exemplo: limite 2000"

        if limite < 0:
            return "❌ O limite não pode ser negativo."

        definir_limite(telefone, limite)

        return (
            "🎯 LIMITE MENSAL DEFINIDO!\n\n"
            f"💰 Limite: R$ {limite:.2f}"
        )

    # =========================
    # REGISTRAR GASTO
    # =========================
    if mensagem.startswith("gastei"):

        texto = mensagem[6:].strip()

        padrao = r"^(\d+(?:[.,]\d{1,2})?)\s+(.+)$"

        resultado = re.match(padrao, texto)

        if not resultado:
            return (
                "❌ Não consegui entender.\n\n"
                "Use assim:\n"
                "*gastei 35,90 mercado*"
            )

        valor_texto = resultado.group(1)
        descricao = resultado.group(2)

        valor = float(valor_texto.replace(",", "."))

        if valor <= 0:
            return "❌ O valor precisa ser maior que zero."

        registrar_gasto(
            telefone,
            valor,
            descricao,
            None
        )

        limite, gasto, disponivel = obter_saldo(telefone)

        return (
            "✅ GASTO REGISTRADO!\n\n"
            f"💰 Valor: R$ {valor:.2f}\n"
            f"📝 Descrição: {descricao}\n\n"
            f"🎯 Limite: R$ {limite:.2f}\n"
            f"💸 Gasto no mês: R$ {gasto:.2f}\n"
            f"💳 Disponível: R$ {disponivel:.2f}"
        )

    # =========================
    # SALDO
    # =========================
    if mensagem == "saldo":

        limite, gasto, disponivel = obter_saldo(telefone)

        return (
            "📊 SEU RESUMO\n\n"
            f"🎯 Limite: R$ {limite:.2f}\n"
            f"💸 Gasto no mês: R$ {gasto:.2f}\n"
            f"💳 Disponível: R$ {disponivel:.2f}"
        )

    # =========================
    # AJUDA / MENU
    # =========================
    if mensagem in [
        "ajuda",
        "menu",
        "oi",
        "olá",
        "ola"
    ]:

        return (
            "🤖 BOT FINANCEIRO\n\n"
            "Comandos disponíveis:\n\n"
            "🎯 *limite 2000*\n"
            "💰 *gastei 35,90 mercado*\n"
            "📊 *saldo*\n"
            "📋 *gastos*\n"
            "🗑️ *apagar 2*\n"
            "🧹 *apagar tudo*\n"
            "❌ *cancelar*\n"
            "🧹 *limpar*\n"
            "❓ *ajuda*"
        )

    # =========================
    # COMANDO NÃO RECONHECIDO
    # =========================
    return (
        "🤖 Não entendi sua mensagem.\n\n"
        "Digite *ajuda* para ver os comandos."
    )