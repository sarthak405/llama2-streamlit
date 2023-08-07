import streamlit as st
# import replicate
import os
import requests

reqUrl = st.secrets['reqUrl']

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

    # headersList = {
    #  "Accept": "*/*",
    #  "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    #  "Content-Type": "multipart/form-data; boundary=kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A" 
    # }

    # App title
    st.set_page_config(page_title="🐝🦙💬 IBM Llama 2 Chatbot")

    # Replicate Credentials
    with st.sidebar:
        st.title('🐝🦙💬 IBM Llama 2 Chatbot')
        # if 'REPLICATE_API_TOKEN' in st.secrets:
        #     st.success('API key already provided!', icon='✅')
        #     replicate_api = st.secrets['REPLICATE_API_TOKEN']
        # else:
        #     replicate_api = st.text_input('Enter Replicate API token:', type='password')
        #     if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
        #         st.warning('Please enter your credentials!', icon='⚠️')
        #     else:
        #         st.success('Proceed to entering your prompt message!', icon='👉')
        # st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
    # os.environ['REPLICATE_API_TOKEN'] = replicate_api

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
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        # output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
        #                        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
        #                               "temperature":0.1, "top_p":0.9, "max_length":512, "repetition_penalty":1})
        prompt = f"{string_dialogue} {prompt_input} Assistant: "
        # payload = f'--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"prompt\"\r\n\r\n{prompt}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n'
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Streamlit',
        }
        files = {
            'prompt': (None, f'{prompt}'),
        }

        response = requests.get(reqUrl, headers=headers, files=files)
        # response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
        # print(prompt)
        # output = "Sample Output. To be replaced by API Call"
        print(response.text)
        return response.text

    # User-provided prompt
    # if prompt := st.chat_input(disabled=not replicate_api):
    if prompt := st.chat_input(disabled=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                if response.startswith('"'):
                    response = response[1:]
                if response.endswith('"'):
                    response = response[:-1]
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    # placeholder.write(full_response)
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
                # placeholder.write(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
