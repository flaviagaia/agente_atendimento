from __future__ import annotations

import json
from pathlib import Path

from src.agent import ask_support_agent
from src.sample_data import ensure_sample_data


def main() -> None:
    ensure_sample_data()
    result = ask_support_agent(
        ticket_id="SUP-1001",
        user_question="Como devemos responder esse cliente e qual time deveria assumir o caso?",
    )
    output_path = Path(__file__).resolve().parent / "data" / "processed" / "support_agent_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    response = result["structured_response"]
    print("Agente Atendimento")
    print(f"runtime_mode: {result['runtime_mode']}")
    print(f"ticket_id: {response['ticket_id']}")
    print(f"category: {response['category']}")
    print(f"priority: {response['priority']}")
    print(f"recommended_team: {response['recommended_team']}")
    print(f"output_path: {output_path}")


if __name__ == "__main__":
    main()
