import streamlit as st
import os
import requests

url_llama2_7b = st.secrets['url_llama2_7b']
url_llama2_13b = st.secrets['url_llama2_13b']
url_llama2_70b = st.secrets['url_llama2_70b']
if 'option' not in st.session_state:
    st.session_state.option = ''

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    # App title
    st.set_page_config(page_title="🐝🦙💬 IBM Llama 2 Chatbot")
    url_mapping = {"Llama2-7b":url_llama2_7b, "Llama2-13b":url_llama2_13b, "Llama2-70b":url_llama2_70b}
    with st.sidebar:
        st.title('🐝🦙💬 IBM Llama 2 Chatbot')
        option = st.selectbox(
            'Model to be run',
            ('Llama2-7b', 'Llama2-13b', 'Llama2-70b'))
        if option != st.session_state.option:
            st.session_state.option = option
            st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
            st.session_state.model_url = url_mapping[option]


    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # Function for generating LLaMA2 response
    # Refactored from https://github.com/a16z-infra/llama2-chatbot
    def generate_llama2_response(prompt_input):
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "[User:] " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "[Assistant:] " + dict_message["content"] + "\n\n"
        prompt = f"{string_dialogue} {prompt_input} [Assistant:] "
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Streamlit',
        }
        files = {
            'prompt': (None, f'{prompt}'),
        }
        reqUrl = st.session_state.model_url
        # response = "Checking Response from {}".format(reqUrl)
        # return response
        response = requests.get(reqUrl, headers=headers, files=files)
        return response.json()['response'].split("[Assistant:]")[-1]

    # User-provided prompt

    if prompt := st.chat_input(disabled=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)

                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)