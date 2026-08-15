# General Assistant with Current Memory
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

def trim_history(messages, max_len=6):
    if len(messages) > max_len:
        return [messages[0]] + messages[-(max_len - 1):]
    return messages

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

    questions = [
        "What's on my calendar today?",
        "Tell me about the standup.",
        "What time is my dentist?",
        "Am I free at 3 pm?",
        "Summarize my day.",
    ]
    
    for question in questions:
        messages.append({"role": "user", "content": question})
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
            messages = trim_history(messages=messages, max_len=6)

            if finish_reason == 'stop':
                print(f"Question: {question}")
                print(f"Answer: {message.content}")
                print(f"Messages in history: {len(messages)}")
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

# Before memory truncation
# Question: What's on my calendar today?
# Answer: I see you have a scheduled breakfast at 10 am and lunch at 2 pm today.
# Messages in history: 5
# Question: Tell me about the standup.
# Answer: Could you please provide more context about which standup you are referring to? Are you asking about a specific meeting, presentation, or something else?
# Messages in history: 7
# Question: What time is my dentist?
# Answer: I can check your calendar for that, but could you please tell me the date you are asking about?
# Messages in history: 9
# Question: Am I free at 3 pm?
# Answer: I checked your calendar for today, and I see you have breakfast at 10 am and lunch at 2 pm.
# I don't see any other events scheduled for 3 pm, so you should be free then!
# Messages in history: 13
# Question: Summarize my day.
# Answer: Based on what I have, your schedule for today includes:
# *   **10:00 AM:** Breakfast
# *   **2:00 PM:** Lunch
# You are free at 3:00 PM according to the current schedule!
# Messages in history: 15

# After memoty truncation
# Question: What's on my calendar today?
# Answer: The events on your calendar for today are: Breakfast at 10am and Lunch at 2pm.
# Messages in history: 5
# Question: Tell me about the standup.
# Answer: Could you please specify which standup you are referring to? I need more context to tell you about it.
# Messages in history: 6
# Question: What time is my dentist?
# Answer: I do not see a dentist appointment scheduled in the calendar for today. Is there another day you are referring to, or perhaps you could provide more details?
# Messages in history: 6
# Question: Am I free at 3 pm?
# Answer: I'm not sure whose schedule you are referring to. Could you please tell me whose availability you'd like me to check?
# Messages in history: 6
# Question: Summarize my day.
# Answer: I would be happy to summarize your day, but I need more information! Could you tell me what specific information you are referring to? For example, are you asking about:
# 1.  Your schedule?
# 2.  A specific period of time?
# 3.  Something else entirely?
# Messages in history: 6