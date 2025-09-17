import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Sprouts Test UI", page_icon="🌱", layout="centered")

st.title("🌱 Sprouts Chat (Test UI)")
st.caption("Chat demo for the Sprouts API")

if st.sidebar.button("Health Check"):
    try:
        r = requests.get(f"{API_BASE}/health", timeout=10)
        st.sidebar.success(r.json())
    except Exception as e:
        st.sidebar.error(str(e))

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message…")
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    try:
        body = {"messages": st.session_state.messages}
        r = requests.post(f"{API_BASE}/ask", json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        reply = data.get("message", "(no message)")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
    except Exception as e:
        err = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": err})
        with st.chat_message("assistant"):
            st.error(err)


