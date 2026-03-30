from __future__ import annotations

import unittest

from src.agent import ask_support_agent
from src.sample_data import ensure_sample_data
from src.tools import classify_service_request, define_next_steps


class SupportAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        ensure_sample_data()

    def test_classification_returns_expected_keys(self) -> None:
        routing = classify_service_request("SUP-1001")
        self.assertIn("category", routing)
        self.assertIn("priority", routing)
        self.assertIn("recommended_team", routing)

    def test_next_steps_returns_sla(self) -> None:
        steps = define_next_steps("SUP-1002")
        self.assertIn("next_steps", steps)
        self.assertIn("sla_bucket", steps)

    def test_agent_returns_structured_response(self) -> None:
        result = ask_support_agent(
            ticket_id="SUP-1003",
            user_question="Como devemos atender esse cliente?",
        )
        self.assertIn("runtime_mode", result)
        self.assertIn("structured_response", result)
        self.assertIn("ticket_id", result["structured_response"])


if __name__ == "__main__":
    unittest.main()
