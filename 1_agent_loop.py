# Single and Multi Turn Conversation
import openai
import os
import json

base_url = "http://127.0.0.1:1234/v1"
model = "google/gemma-4-e2b"

try:
    api_key = os.environ.get("OPENAI_API_KEY", model)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    messages = [
            {"role": "system", "content": "You are a helpful assistant who provides brief responses."},
    ]

    ### Single Turn
    # messages.append({"role": "user", "content": "Operations that AI Agent can perform"})

    # while True:
    #     response = client.chat.completions.create(
    #         model=model,
    #         messages=messages,
    #     )
    #     finish_reason = response.choices[0].finish_reason
    #     if finish_reason == 'stop':
    #         print(response.choices[0].message.content)
    #         break
    #     else:
    #         break

    ### Multi Turn
    questions = [
            "Define AI Agent",
            "AI Agent vs AI Chatbot",
            "Explain with example",
    ]

    for question in questions:
        messages.append({"role": "user", "content": question})
        while True:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            finish_reason = response.choices[0].finish_reason
            if finish_reason == 'stop':
                content = response.choices[0].message.content
                print(f"Question: {question}")
                print(f"Answer: {content}")
                messages.append({"role": "assistant", "content": content})
                break
            else:
                break

except openai.AuthenticationError:
    print("error: OpenAI Authentication Error. Check your API key.")
except openai.APIError as e:
    print(f"error: OpenAI API Error: {e}")
except Exception as e:
    print(f"error: An unexpected error occurred: {e}")

# Output

# Single Turn
# *   **Data Processing:** Analyzing large datasets, extracting information, and summarizing text.
# *   **Task Automation:** Performing repetitive tasks like scheduling, data entry, or email drafting.
# *   **Information Retrieval:** Searching the internet or internal databases for specific answers.
# *   **Decision Making:** Classifying inputs, making recommendations, or routing decisions based on rules.
# *   **Natural Language Processing (NLP):** Understanding and generating human language (chatbots, translation).
# *   **API Interaction:** Connecting to and operating external software services.

# Multi Turn
# Question: Define AI Agent
# Answer: An AI agent is an entity that perceives its environment, processes that information (reasons), and takes actions to achieve a specific goal.
# Question: AI Agent vs AI Chatbot
# Answer: **AI Agent:**
# *   **Focus:** Achieving complex, multi-step goals autonomously.
# *   **Function:** Perceives the environment, plans actions, executes tasks, and adapts over time.
# *   **Key Feature:** Autonomy and proactive decision-making.
# **AI Chatbot:**
# *   **Focus:** Conversational interaction and natural language understanding (NLU).
# *   **Function:** Responds to prompts, answers questions, and maintains a dialogue.
# *   **Key Feature:** Dialogue and information retrieval.
# **In short:** A Chatbot *talks* to you; an Agent *does* things for you.
# Question: Explain with example
# Answer: **Scenario: Planning a Vacation**
# **1. AI Chatbot Example (Reactive):**
# *   **You say:** "What are the best beaches in Thailand?"
# *   **Chatbot responds:** It immediately searches its database and lists three popular beach destinations, providing static information.
# *   **Limitation:** It can only answer questions it was explicitly trained to answer; it cannot independently book anything.
# **2. AI Agent Example (Proactive/Goal-Oriented):**
# *   **You say:** "Plan a 5-day budget trip to Phuket for next month, focusing on budget accommodation and included tours."
# *   **Agent does:**
#     1.  **Perceives Goal:** Identifies the constraints (5 days, Phuket, budget).
#     2.  **Plans:** Searches flight prices, compares hotel reviews, finds tour packages, and builds a daily itinerary.
#     3.  **Acts:** Book/suggests the actual combination of flights, hotels, and activities.
# *   **Key Difference:** The Agent *takes initiative* to complete the entire objective, not just provide an answer.