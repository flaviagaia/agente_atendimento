from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from .tools import classify_service_request, compliance_guardrail, define_next_steps, draft_support_response, get_ticket_context

try:
    from pydantic_ai import Agent, RunContext
except Exception:  # pragma: no cover - optional dependency
    Agent = None
    RunContext = None


@dataclass
class TicketDeps:
    ticket_id: str


class SupportResponse(BaseModel):
    ticket_id: str
    category: str = Field(description="Categoria principal da solicitação.")
    priority: str = Field(description="Prioridade operacional do atendimento.")
    recommended_team: str = Field(description="Time responsável sugerido.")
    response_to_customer: str = Field(description="Resposta customer-facing consolidada.")
    next_steps: list[str] = Field(description="Próximos passos operacionais.")
    sla_bucket: str = Field(description="Faixa de SLA sugerida.")
    guardrail: str = Field(description="Mensagem de compliance e comunicação segura.")


SYSTEM_PROMPT = """
Você é um agente de atendimento inteligente.

Seu trabalho é:
- interpretar o ticket do cliente;
- classificar categoria e prioridade;
- definir o time recomendado;
- redigir uma resposta inicial clara e empática;
- listar próximos passos;
- respeitar linguagem segura, sem promessas indevidas.

Sempre use as ferramentas disponíveis antes de responder.
"""


def _build_pydantic_agent(model_name: str = "openai:gpt-4.1-mini"):
    if not (Agent and os.getenv("OPENAI_API_KEY")):
        return None

    agent = Agent(
        model_name,
        deps_type=TicketDeps,
        output_type=SupportResponse,
        system_prompt=SYSTEM_PROMPT,
    )

    @agent.tool
    def get_ticket(ctx: RunContext[TicketDeps]) -> dict[str, Any]:
        return get_ticket_context(ctx.deps.ticket_id)

    @agent.tool
    def classify_ticket(ctx: RunContext[TicketDeps]) -> dict[str, Any]:
        return classify_service_request(ctx.deps.ticket_id)

    @agent.tool
    def draft_reply(ctx: RunContext[TicketDeps]) -> str:
        return draft_support_response(ctx.deps.ticket_id)

    @agent.tool
    def get_steps(ctx: RunContext[TicketDeps]) -> dict[str, Any]:
        return define_next_steps(ctx.deps.ticket_id)

    @agent.tool
    def get_guardrail(_: RunContext[TicketDeps], topic: str) -> str:
        return compliance_guardrail(topic)

    return agent


def _build_fallback_response(ticket_id: str, user_question: str) -> SupportResponse:
    routing = classify_service_request(ticket_id)
    steps = define_next_steps(ticket_id)
    return SupportResponse(
        ticket_id=ticket_id,
        category=routing["category"],
        priority=routing["priority"],
        recommended_team=routing["recommended_team"],
        response_to_customer=draft_support_response(ticket_id),
        next_steps=steps["next_steps"],
        sla_bucket=steps["sla_bucket"],
        guardrail=compliance_guardrail(user_question),
    )


async def _run_pydantic_agent(ticket_id: str, user_question: str, model_name: str) -> dict[str, Any]:
    agent = _build_pydantic_agent(model_name=model_name)
    ticket = get_ticket_context(ticket_id)

    if agent is None:
        response = _build_fallback_response(ticket_id=ticket_id, user_question=user_question)
        return {
            "runtime_mode": "deterministic_fallback",
            "ticket": ticket,
            "structured_response": response.model_dump(),
        }

    prompt = (
        f"ticket_id={ticket_id}\n"
        f"user_question={user_question}\n"
        "Produza uma resposta estruturada com classificação, encaminhamento, próximos passos e resposta ao cliente."
    )
    try:
        result = await agent.run(prompt, deps=TicketDeps(ticket_id=ticket_id))
        output = result.output
        return {
            "runtime_mode": "pydantic_ai_agent",
            "ticket": ticket,
            "structured_response": output.model_dump(),
        }
    except Exception:
        response = _build_fallback_response(ticket_id=ticket_id, user_question=user_question)
        return {
            "runtime_mode": "deterministic_fallback",
            "ticket": ticket,
            "structured_response": response.model_dump(),
        }


def ask_support_agent(
    ticket_id: str,
    user_question: str,
    model_name: str = "openai:gpt-4.1-mini",
) -> dict[str, Any]:
    return asyncio.run(_run_pydantic_agent(ticket_id=ticket_id, user_question=user_question, model_name=model_name))
