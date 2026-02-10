# streamlit_app.py
import streamlit as st
from core.platform import Platform
from core.runner import Runner

st.set_page_config(page_title="MedRouter AI", page_icon="🧠", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .status-badge { padding: 4px 10px; border-radius: 10px; font-size: 12px; font-weight: bold; color: white; margin-right: 8px; }
    .edge-bg { background-color: #2E7D32; }
    .fog-bg { background-color: #1565C0; }
    .cloud-bg { background-color: #6A1B9A; }
    </style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.platform = Platform()
    st.session_state.runner = Runner(st.session_state.platform)
    st.session_state.history = []

st.title("🧠 Medical Intelligence Router")

# Display Chat
for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        if chat["role"] == "assistant":
            color = f"{chat['layer'].lower()}-bg"
            st.markdown(f"<span class='status-badge {color}'>{chat['layer']}</span> <small>{chat['reason']}</small>", unsafe_allow_html=True)
            st.write(chat["text"])
            st.caption(f"⏱️ Latency: {chat['latency']}ms")
        else:
            st.write(chat["text"])

# Input
if prompt := st.chat_input("Posez votre question médicale..."):
    st.session_state.history.append({"role": "user", "text": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Routage en cours..."):
            res = st.session_state.runner.dispatch(prompt)
            color = f"{res['layer'].lower()}-bg"
            st.markdown(f"<span class='status-badge {color}'>{res['layer']}</span> <small>{res['reason']}</small>", unsafe_allow_html=True)
            st.write(res["text"])
            st.caption(f"⏱️ Latency: {res['latency_ms']}ms")
            
            st.session_state.history.append({
                "role": "assistant", "text": res["text"], "layer": res["layer"],
                "reason": res["reason"], "latency": res["latency_ms"]
            })