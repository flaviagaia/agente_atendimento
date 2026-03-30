from __future__ import annotations

from typing import Any

from .sample_data import load_ticket


def get_ticket_context(ticket_id: str) -> dict[str, Any]:
    """Retorna o ticket estruturado consultado pelo agente."""
    return load_ticket(ticket_id)


def classify_service_request(ticket_id: str) -> dict[str, Any]:
    """Classifica categoria, urgência e time recomendado com heurísticas simples."""
    ticket = load_ticket(ticket_id)
    message = f"{ticket['subject']} {ticket['message']}".lower()

    if "cobran" in message or ticket["product_area"] == "billing":
        category = "financeiro"
        team = "billing_ops"
    elif "acess" in message or "login" in message or ticket["product_area"] == "login":
        category = "acesso"
        team = "identity_support"
    elif ticket["product_area"] == "feature_request":
        category = "produto"
        team = "product_ops"
    else:
        category = "geral"
        team = "customer_support"

    priority_score = 0
    priority_score += 2 if ticket["priority_hint"] == "alta" else 1 if ticket["priority_hint"] == "media" else 0
    priority_score += 1 if ticket["customer_tier"] in {"premium", "business"} else 0
    priority_score += 1 if int(ticket["open_days"]) >= 5 else 0
    priority_score += 1 if ticket["sentiment"] in {"frustrated", "anxious"} else 0

    if priority_score >= 4:
        priority = "alta"
    elif priority_score >= 2:
        priority = "media"
    else:
        priority = "baixa"

    return {
        "ticket_id": ticket_id,
        "category": category,
        "priority": priority,
        "recommended_team": team,
        "priority_score": priority_score,
    }


def draft_support_response(ticket_id: str) -> str:
    """Gera uma resposta inicial grounded no tipo de solicitação."""
    ticket = load_ticket(ticket_id)
    routing = classify_service_request(ticket_id)

    if routing["category"] == "financeiro":
        return (
            f"Olá, {ticket['customer_name']}. Identificamos sua solicitação relacionada a cobrança. "
            "Vamos validar a duplicidade informada e orientar o fluxo de estorno ou ajuste financeiro."
        )
    if routing["category"] == "acesso":
        return (
            f"Olá, {ticket['customer_name']}. Vamos apoiar a recuperação do acesso com foco em verificação "
            "de identidade e reativação segura da conta."
        )
    if routing["category"] == "produto":
        return (
            f"Olá, {ticket['customer_name']}. Obrigado pela sugestão. Vamos registrar a necessidade e "
            "encaminhar o pedido para avaliação do time de produto."
        )
    return (
        f"Olá, {ticket['customer_name']}. Recebemos sua solicitação e vamos direcioná-la ao time mais adequado."
    )


def define_next_steps(ticket_id: str) -> dict[str, Any]:
    """Organiza próximos passos operacionais para o atendimento."""
    routing = classify_service_request(ticket_id)

    if routing["category"] == "financeiro":
        steps = [
            "validar histórico transacional e duplicidade",
            "confirmar status do pagamento com o processador",
            "executar ou acompanhar fluxo de estorno",
        ]
    elif routing["category"] == "acesso":
        steps = [
            "confirmar identidade do cliente",
            "verificar status do método de autenticação",
            "executar recuperação de acesso segura",
        ]
    elif routing["category"] == "produto":
        steps = [
            "registrar demanda estruturada",
            "agrupar com feedbacks similares",
            "encaminhar para backlog ou discovery",
        ]
    else:
        steps = [
            "classificar corretamente a demanda",
            "direcionar ao time responsável",
            "acompanhar SLA inicial",
        ]

    return {
        "ticket_id": ticket_id,
        "next_steps": steps,
        "sla_bucket": "24h" if routing["priority"] == "alta" else "72h" if routing["priority"] == "media" else "120h",
    }


def compliance_guardrail(topic: str) -> str:
    """Reforça linguagem segura e sem promessas indevidas."""
    return (
        "Guardrail de atendimento: comunicar o próximo passo com clareza, sem prometer resolução fora da política "
        f"ou do SLA. Contexto consultado: {topic}."
    )
