from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
TICKETS_PATH = RAW_DIR / "service_tickets.csv"


DEFAULT_TICKETS = [
    {
        "ticket_id": "SUP-1001",
        "customer_name": "Mariana Souza",
        "channel": "chat",
        "product_area": "billing",
        "subject": "Cobrança em duplicidade no cartão",
        "message": "Recebi duas cobranças no mesmo dia referentes à mesma assinatura e preciso entender como será o estorno.",
        "priority_hint": "alta",
        "sentiment": "frustrated",
        "customer_tier": "premium",
        "open_days": 1,
    },
    {
        "ticket_id": "SUP-1002",
        "customer_name": "Carlos Mendes",
        "channel": "email",
        "product_area": "login",
        "subject": "Não consigo acessar minha conta",
        "message": "Troquei de celular e agora o código de verificação não chega. Preciso recuperar o acesso.",
        "priority_hint": "alta",
        "sentiment": "anxious",
        "customer_tier": "standard",
        "open_days": 0,
    },
    {
        "ticket_id": "SUP-1003",
        "customer_name": "Fernanda Rocha",
        "channel": "portal",
        "product_area": "feature_request",
        "subject": "Exportação de relatórios em CSV",
        "message": "Seria muito útil poder exportar os relatórios mensais em CSV para o time financeiro.",
        "priority_hint": "media",
        "sentiment": "neutral",
        "customer_tier": "business",
        "open_days": 6,
    },
]


def ensure_sample_data() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not TICKETS_PATH.exists():
        pd.DataFrame(DEFAULT_TICKETS).to_csv(TICKETS_PATH, index=False)
    return pd.read_csv(TICKETS_PATH)


def load_tickets() -> pd.DataFrame:
    return ensure_sample_data()


def load_ticket(ticket_id: str) -> dict:
    tickets = ensure_sample_data()
    match = tickets.loc[tickets["ticket_id"] == ticket_id]
    if match.empty:
        raise KeyError(f"Ticket id not found: {ticket_id}")
    return match.iloc[0].to_dict()
