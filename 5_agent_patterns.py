# Research with Structed Output, Input Guardrails and Human in the Loop 
import openai
import os
import json

base_url = "http://127.0.0.1:1234/v1"
# Model Component
model = "google/gemma-4-e2b"
user_message = "Email Jill my calendar summary for today?"

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def send_email(to, subject, body):
    return f"Email sent to {to}"

def execute_tool(name, args):
    result = None
    if name == "check_calendar":
        result = check_calendar(**args)
    elif name == "send_email":
        print(f"Proposed email: {args}")
        confirm = input("Send this email? (y/n): ")
        if confirm.lower() != "y":
            result = "Email cancelled by user"
        else:
            result = send_email(**args)
    return result if result else f"Unkown tool: {name}"

def check_input(message):
    blocked = ["medical", "legal", "financial advice"]
    for term in blocked:
        if term in message.lower():
            return "I can only help with scheduling and contacts"
    return None

try:
    api_key = os.environ.get("OPENAI_API_KEY", model)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    # System Prompt Component
    messages = [
            {"role": "system", "content": """
            You are a scheduling assistant. 
            Use the ReAct pattern.
            Thought: reason about what to do next.
            Action: call a tool if needed.
            Repeat until you can give a final answer
            Always end your final response with a JSON summary block:
            {"summary": "...".
            "actions_taken":["..."]}
            """},
    ]

    # Tool Component
    tools = [
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
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send Email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            }
        ]

    guard_result = check_input(user_message)
    if guard_result:
        # no llm call
        print(guard_result)
    else:
        messages.append({"role": "user", "content": user_message})
        # Orchestration Component (Loop)
        while True:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
            )

            finish_reason = response.choices[0].finish_reason
            message = response.choices[0].message
            # Memory Component
            messages.append(message)

            if finish_reason == 'stop':
                print(message.content)
                break
            elif response.choices[0].finish_reason == "tool_calls":
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    result = execute_tool(name, arguments)
                    messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result
                            }
                        )
            else:
                break

except openai.AuthenticationError:
    print("error: OpenAI Authentication Error. Check your API key.")
except openai.APIError as e:
    print(f"error: OpenAI API Error: {e}")
except Exception as e:
    print(f"error: An unexpected error occurred: {e}")

# Output
# Proposed email: {'body': 'Here is my calendar summary for today: 10am: Breakfast, 2pm: Lunch.', 'subject': 'Calendar Summary for Today', 'to': 'Jill'}
# Send this email? (y/n): y
# {"summary": "Calendar summary for today (10am: Breakfast, 2pm: Lunch) has been successfully emailed to Jill.", "actions_taken": ["check_calendar", "send_email"]}