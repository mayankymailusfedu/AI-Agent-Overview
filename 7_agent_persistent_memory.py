# Research with Persistent Memory
import openai
import os
import json

base_url = "http://127.0.0.1:1234/v1"
# Model Component
model = "google/gemma-4-12b-qat"
user_message = "Schedule a meeting for today with Jill"
max_itr = 10
memory_file = "agent_memory.json"

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def send_email(to, subject, body):
    return f"Email sent to {to}"

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
        return f"Unkown tool: {name}"
    except Exception as e:
        return f"Error: {str(e)}. Try a different approach."

def check_input(message):
    blocked = ["medical", "legal", "financial advice"]
    for term in blocked:
        if term in message.lower():
            return "I can only help with scheduling and contacts"
    return None

def load_memory():
    if not os.path.exists(memory_file):
        return {}
    with open(memory_file, 'r') as f:
        return json.load(f)

def save_memory(data):
    with open(memory_file, 'w') as f:
        json.dump(data, f, indent=2)
    
try:
    api_key = os.environ.get("OPENAI_API_KEY", model)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    # System Prompt Component
    messages = [
            {"role": "system", "content": "You are a helpful personal assistant."},
    ]

    memory = load_memory()
    if memory:
       # System Prompt Component
        messages = [
                {"role": "system", "content": f"You are a helpful personal assistant. \n Known user preferences: {json.dumps(memory)}"},
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
# Iteration 0/10
# 10am: Breakfast, 2pm: Lunch
# Iteration 1/10
# I see you have "Breakfast" at 10 am and "Lunch" at 2 pm today. Since you prefer afternoon meetings, would you like me to schedule the meeting with Jill for 3:00 pm, or is there another time you'd prefer?