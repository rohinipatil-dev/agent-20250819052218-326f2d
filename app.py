import streamlit as st
from openai import OpenAI

# -------------------------------
# Configuration and Initialization
# -------------------------------

st.set_page_config(page_title="Programmer Joke Bot", page_icon="🤖", layout="centered")

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "tone" not in st.session_state:
        st.session_state.tone = "Witty"
    if "length" not in st.session_state:
        st.session_state.length = "Short (1-3 lines)"
    if "language" not in st.session_state:
        st.session_state.language = "English"

init_session_state()

# Initialize OpenAI client
client = OpenAI()

# -------------------------------
# Helpers
# -------------------------------

def build_system_messages(tone: str, length: str, language: str):
    base = {"role": "system", "content": "You are a helpful assistant."}
    policy = {
        "role": "system",
        "content": (
            f"You are a witty stand-up comedian who specializes in programming jokes. "
            f"Constraints and style:\n"
            f"- Tone: {tone}\n"
            f"- Preferred length: {length}\n"
            f"- Primary language: {language}\n"
            f"- Keep jokes original, inclusive, and family-friendly.\n"
            f"- Avoid offensive, derogatory, or discriminatory content.\n"
            f"- Keep references technically accurate. If asked, briefly explain the punchline.\n"
            f"- If the user drifts off-topic, gently bring it back to programming humor."
        )
    }
    return [base, policy]

def call_model(system_messages, conversation_messages, temperature=0.9, max_tokens=300):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=system_messages + conversation_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I ran into an error: {e}"

def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def render_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -------------------------------
# Sidebar Controls
# -------------------------------

with st.sidebar:
    st.header("Settings")
    st.session_state.tone = st.selectbox(
        "Tone",
        options=["Witty", "Dry", "Playful", "Deadpan", "Pun-heavy", "Light and friendly"],
        index=["Witty", "Dry", "Playful", "Deadpan", "Pun-heavy", "Light and friendly"].index(st.session_state.tone)
    )
    st.session_state.length = st.selectbox(
        "Length",
        options=["One-liner", "Short (1-3 lines)", "Medium (4-6 lines)"],
        index=["One-liner", "Short (1-3 lines)", "Medium (4-6 lines)"].index(st.session_state.length)
    )
    st.session_state.language = st.selectbox(
        "Language",
        options=["English", "Spanish", "German", "French", "Portuguese", "Italian", "Japanese", "Korean", "Chinese"],
        index=["English", "Spanish", "German", "French", "Portuguese", "Italian", "Japanese", "Korean", "Chinese"].index(st.session_state.language)
    )
    st.divider()
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.experimental_rerun()

# -------------------------------
# Main UI
# -------------------------------

st.title("🤖 Programmer Joke Bot")
st.caption("Ask me for programming jokes, roast your stack (kindly), or request a punny one-liner.")

# Starter suggestions
if not st.session_state.messages:
    with st.expander("Suggestions"):
        cols = st.columns(2)
        with cols[0]:
            if st.button("Tell me a one-liner about Python"):
                add_message("user", "Tell me a one-liner about Python.")
        with cols[1]:
            if st.button("Make a JavaScript callback joke"):
                add_message("user", "Make a JavaScript callback joke.")
        cols2 = st.columns(2)
        with cols2[0]:
            if st.button("Roast my code gently"):
                add_message("user", "Roast my code gently, but keep it friendly and humorous.")
        with cols2[1]:
            if st.button("Explain a regex joke"):
                add_message("user", "Tell me a regex joke and then explain the punchline briefly.")
        if any(btn for btn in [st.session_state.messages]):
            st.experimental_rerun()

# Render existing history
render_chat_history()

# Chat input
user_input = st.chat_input("Ask for a programming joke or give a topic...")
if user_input:
    add_message("user", user_input)

# If there is a new user message, get a response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Crafting a joke..."):
            sys_msgs = build_system_messages(
                tone=st.session_state.tone,
                length=st.session_state.length,
                language=st.session_state.language
            )
            reply = call_model(sys_msgs, st.session_state.messages)
            add_message("assistant", reply)
            st.markdown(reply)