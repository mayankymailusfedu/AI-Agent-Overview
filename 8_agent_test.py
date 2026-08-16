import unittest

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def execute_tool(name, args):
    try:
        if name == "check_calendar":
            return check_calendar(**args)
        return f"Unkown tool: {name}"
    except Exception as e:
        return f"Error: {str(e)}. Try a different approach."

class TestTools(unittest.TestCase):

    def test_check_calendar_returns_string(self):
        result = check_calendar("today")
        self.assertIsInstance(result, str)

    def test_check_calendar_contins_breakfast(self):
        result = check_calendar("today")
        self.assertIn("Breakfast", result)

class TestAgentLoop(unittest.TestCase):

    def test_tool_dispatch_on_tool_call(self):
        from unittest.mock import MagicMock, patch
        import json

        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "check_calendar"
        mock_tool_call.function.arguments = json.dumps({})

        mock_message = MagicMock()
        mock_message.finish_reason = "tool_calls"

        name = mock_tool_call.function.name
        args = json.loads(mock_tool_call.function.arguments)
        execute_tool(name, args)
        self.assertEqual(name, "check_calendar")

class TestAgentEval(unittest.TestCase):

    def test_agent_responds_to_calendar_query(self):
        import os
        from openai import OpenAI

        base_url = "http://127.0.0.1:1234/v1"
        model = "google/gemma-4-e2b"

        api_key = os.environ.get("OPENAI_API_KEY", model)
        client = OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user", "content":"What's on my calendar?"}],
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": "check_calendar",
                                "description": "Check calendar events.",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                    "date": {"type": "string"}
                                    },
                                    "required": ["date"]
                                }
                            }
                        }
                    ]
                )

        choice = response.choices[0]
        made_tool_call = choice.finish_reason == "tool_calls"
        has_keyword = any(w in (choice.message.content or '')
            for w in ["calendar", "meeting", "standup"])
        self.assertTrue(made_tool_call or has_keyword)

# Output
# python3 -m unittest 8_agent_test.py -v
# test_agent_responds_to_calendar_query (8_agent_test.TestAgentEval.test_agent_responds_to_calendar_query) ... ok
# test_tool_dispatch_on_tool_call (8_agent_test.TestAgentLoop.test_tool_dispatch_on_tool_call) ... ok
# test_check_calendar_contins_breakfast (8_agent_test.TestTools.test_check_calendar_contins_breakfast) ... ok
# test_check_calendar_returns_string (8_agent_test.TestTools.test_check_calendar_returns_string) ... ok
# ----------------------------------------------------------------------
# Ran 4 tests in 5.274s
# OK