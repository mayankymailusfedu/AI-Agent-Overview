# Research with Monitoring
import openai
import os
import json
import time

base_url = "http://127.0.0.1:1234/v1"
# Model Component
model = "google/gemma-4-e2b"
max_itr = 10
run_log = []
total_prompt_tokens = 0
total_completion_tokens = 0

def check_calendar(date):
    return "10am: Breakfast, 2pm: Lunch"

def execute_tool(name, args):
    start_time = time.time()
    result = None
    try:
        if name == "check_calendar":
            result = check_calendar(**args)
        else:
            result = f"Unkown tool: {name}"
    except Exception as e:
        result = f"Error: {str(e)}"
    duration = time.time() - start_time
    run_log.append({
        "tool": name, 
        "args": args,
        "result": result[:100],
        "duration_ms": round(duration * 1000),
    })
    return result

try:
    api_key = os.environ.get("OPENAI_API_KEY", model)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    # System Prompt Component
    messages = [
            {"role": "system", "content": "You are a helpful personal assistant. "
            "Before every tool call, write 'Thought: [your reasoning]'. "
            "After every tool result, write 'Observation: [what your learned]'."
            "Then decide your next step."},
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
    iteration = 0

    wall_start = time.time()

    while(iteration < max_itr):
        print(f"Iteration {iteration}/{max_itr}")

        if iteration >= max_itr - 2:
            print(f"WARNING: approaching iteration limit.")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        if response.usage:
            total_prompt_tokens = total_prompt_tokens + response.usage.prompt_tokens
            total_completion_tokens = total_completion_tokens + response.usage.completion_tokens

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

    elapsed = round(time.time() - wall_start, 2)
    print("\n=== Execution Summary ===")
    print(f"Iteration used: {iteration}/{max_itr}")
    print(f"Total tokens: {total_prompt_tokens + total_completion_tokens}")
    print(f"Tool called: {len(run_log)}")
    for entry in run_log:
        print(f"  - {entry['tool']} : {entry['duration_ms']}ms")
    print(f"Wall-clock time: {elapsed}")

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
# The events on your calendar for today are:
# *   10am: Breakfast
# *   2pm: Lunch
# === Execution Summary ===
# Iteration used: 1/10
# Total tokens: 522
# Tool called: 1
#   - check_calendar : 0ms
# Wall-clock time: 4.21