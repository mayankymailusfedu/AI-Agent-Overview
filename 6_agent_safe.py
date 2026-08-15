# Research with Failure Mode 
import openai
import os
import json

base_url = "http://127.0.0.1:1234/v1"
# Model Component
model = "google/gemma-4-e2b"
user_message = "What is today's news?"
max_itr = 10

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def send_email(to, subject, body):
    return f"Email sent to {to}"

def flaky_tool(query):
    raise Exception("Service unavailable")

def execute_tool(name, args):
    try:
        if name == "check_calendar":
            return check_calendar(**args)
        elif name == "send_email":
            print(f"Proposed email: {args}")
            confirm = input("Send this email? (y/n): ")
            if confirm.lower() != "y":
                return "Email cancelled by user"
            else:
                return send_email(**args)
        elif name == "flaky_tool":
            return flaky_tool(**args)
        return f"Unkown tool: {name}"
    except Exception as e:
        return f"Error: {str(e)}. Try a different approach."

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
            },
            {
                "type": "function",
                "function": {
                    "name": "flaky_tool",
                    "description": "Search",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "query": {"type": "string"}
                        }
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
        iteration = 0
        while(iteration < max_itr):
            print(f"Iteration {iteration}/{max_itr}")
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
                    print(result)
                    messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result
                            }
                        )
            else: 
                break
            iteration = iteration + 1

        if(iteration == max_itr):
            messages.append({"role":"user", "content":"You have reached the max. Give me your best answer."})
            final = client.chat.completions.create(model=model, messages=messages,)
            print(final.choices[0].message.content)


except openai.AuthenticationError:
    print("error: OpenAI Authentication Error. Check your API key.")
except openai.APIError as e:
    print(f"error: OpenAI API Error: {e}")
except Exception as e:
    print(f"error: An unexpected error occurred: {e}")

# Output

# Iteration
# Iteration 0/10
# Error: Service unavailable. Try a different approach.
# Iteration 1/10
# {
# "summary": "I was unable to retrieve today's news because the tool I used returned an error: 'Service unavailable. Try a different approach.'",
# "actions_taken": [
# "flaky_tool(query=\"today's news\")"
# ]
# }
# Iteration 2/10
# Iteration 3/10
# Iteration 4/10
# Iteration 5/10
# Iteration 6/10
# Iteration 7/10
# Iteration 8/10
# Iteration 9/10
# {
# "summary": "I apologize, but I cannot provide you with today's current news because the tool I attempted to use is currently unavailable or returned an error. As a scheduling assistant, my capabilities are limited to the functions of the tools provided, and in this case, I cannot fulfill the request for real-time news.",
# "actions_taken": [
# "Acknowledged failure of previous tool call and provided a final explanation."
# ]
# }

# Error Hanlding
# Iteration 0/10
# Error: Service unavailable. Try a different approach.
# Iteration 1/10
# I am sorry, but I am unable to retrieve real-time news at this moment as the tool I use for searching returned an error. Could you please provide a more specific topic or query if you are looking for information on something else?