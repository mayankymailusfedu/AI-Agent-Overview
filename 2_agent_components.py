# General Assistant 
import openai
import os
import json

base_url = "http://127.0.0.1:1234/v1"
# Model Component
model = "google/gemma-4-e2b"

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def execute_tool(name, args):
    if name == "check_calendar":
        return check_calendar(**args)
    return f"Unkown tool: {name}"

try:
    api_key = os.environ.get("OPENAI_API_KEY", model)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    # System Prompt Component
    messages = [
            {"role": "system", "content": "You are a helpful assistant. Use your tools when you need real data."},
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
            }
        ]

    messages.append({"role": "user", "content": "What's on my calendar today?"})

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
# I see you have a breakfast scheduled for 10 AM and lunch at 2 PM today.