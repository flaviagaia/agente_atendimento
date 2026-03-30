from __future__ import annotations

import streamlit as st

from src.agent import ask_support_agent
from src.sample_data import load_tickets


st.set_page_config(page_title="Agente de Atendimento Inteligente", layout="wide")
st.title("Agente de Atendimento Inteligente")
st.caption("MVP com PydanticAI para classificação, resposta estruturada e próximos passos de atendimento.")

tickets = load_tickets()
options = tickets.set_index("ticket_id")["subject"].to_dict()

with st.sidebar:
    st.header("Stack Técnica")
    st.markdown(
        """
        - `PydanticAI` para orquestração com saída estruturada
        - `BaseModel` como contrato forte de resposta
        - `deps_type` para contexto explícito do ticket
        - tools registradas por decorator
        - fallback determinístico para execução local
        """
    )
    st.header("Premissas do MVP")
    st.markdown(
        """
        - foco em suporte e atendimento inicial
        - resposta grounded no ticket consultado
        - classificação heurística de categoria e prioridade
        - guardrail de comunicação segura
        """
    )

ticket_id = st.selectbox(
    "Selecione o ticket",
    options=list(options.keys()),
    format_func=lambda tid: f"{tid} - {options[tid]}",
)

question = st.text_area(
    "Pergunta operacional",
    value="Como devemos responder esse cliente e qual time deveria assumir o caso?",
    height=120,
)

if st.button("Executar agente", type="primary"):
    result = ask_support_agent(ticket_id=ticket_id, user_question=question)
    response = result["structured_response"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Runtime mode", result["runtime_mode"])
    c2.metric("Categoria", response["category"])
    c3.metric("Prioridade", response["priority"])

    tab1, tab2, tab3 = st.tabs(["Resposta estruturada", "Ticket consultado", "Fluxo operacional"])
    with tab1:
        st.json(response)
    with tab2:
        st.json(result["ticket"])
    with tab3:
        st.write(response["response_to_customer"])
        st.write("Próximos passos:")
        for step in response["next_steps"]:
            st.markdown(f"- {step}")
        st.info(response["guardrail"])

st.divider()
st.subheader("Arquitetura resumida")
st.code(
    """Analista -> PydanticAI Agent -> tools de atendimento -> resposta estruturada tipada
          \\-> fallback determinístico local (sem OPENAI_API_KEY / sem runtime PydanticAI)""",
    language="text",
)
