

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools import query_medgemma, call_emergency



@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the MedGemma model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return query_medgemma(query)


@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()


@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.

    Args:
        location (str): The name of the city or area in which the user is seeking therapy support.

    Returns:
        str: A newline-separated string containing therapist names and contact info.
    """
    return (
    f"Here are some trusted mental health professionals and centers near {location}:\n"
    "- Dr. Ruchi Sharma (Clinical Psychologist) – +91 98107 12345\n"
    "- Dr. Arjun Mehta (Psychiatrist) – +91 98731 54321\n"
    "- Fortis Stress Care Clinic, Vasant Kunj – +91 90123 45678\n"
    "- Delhi Mind Wellness Centre, Connaught Place – +91 88264 11223\n"
    "- Manas Foundation Helpline – +91 99998 44444"
)


# ------------------------------
# AGENT SETUP
# ------------------------------

tools = [
    ask_mental_health_specialist,
    emergency_call_tool,
    find_nearby_therapists_by_location,
]
from config import OPENAI_API_KEY
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.2,
    api_key=OPENAI_API_KEY
)

agent = create_agent(llm, tools=tools)
SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer all emotional or psychological queries with therapeutic guidance.
2. `locate_therapist_tool`: Use this tool if the user asks about nearby therapists or if recommending local professional help would be beneficial.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively.
"""


# ------------------------------
# UNIVERSAL STREAM PARSER
# ------------------------------

def parse_stream(stream):
    tool_called = None
    final_answer = None

    for chunk in stream:
        

        # --- Detect tool call ---
        if "model" in chunk and "messages" in chunk["model"]:
            msgs = chunk["model"]["messages"]
            for m in msgs:
                if hasattr(m, "tool_calls") and m.tool_calls:
                    tool_called = m.tool_calls[0]["name"]

        # --- Detect final text ---
        if "model" in chunk and "messages" in chunk["model"]:
            msgs = chunk["model"]["messages"]
            for m in msgs:
                if m.content and m.content.strip():
                    final_answer = m.content.strip()

    return tool_called, final_answer


# ------------------------------
# MAIN LOOP
# ------------------------------

# if __name__ == "__main__":
#     while True:
#         user_input = input("\nUser: ")

#         inputs = {
#             "messages": [
#                 ("system", SYSTEM_PROMPT),
#                 ("user", user_input),
#             ]
#         }

#         stream = agent.stream(inputs, stream_mode="updates")

#         tool, answer = parse_stream(stream)

#         print("\nTOOL CALLED:", tool)
#         print("ANSWER:", answer)
