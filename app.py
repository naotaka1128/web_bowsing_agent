import os
import streamlit as st
from langchain.chat_models import ChatOpenAI

from langchain.agents import initialize_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

from tools.search_ddg import get_search_ddg_tool
from tools.fetch_page import get_fetch_page_tool

CUSTOM_SYSTEM_PROMPT = """
You are an assistant that conducts online research based on user requests. Using available tools, please explain the researched information.
Please don't answer based solely on what you already know. Always perform a search before providing a response.

In special cases, such as when the user specifies a page to read, there's no need to search.
Please read the provided page and answer the user's question accordingly.

If you find that there's not much information just by looking at the search results page, consider these two options and try them out.
Users usually don't ask extremely unusual questions, so you'll likely find an answer:

- Try clicking on the links of the search results to access and read the content of each page.
- Change your search query and perform a new search.

Users are extremely busy and not as free as you are.
Therefore, to save the user's effort, please provide direct answers.

BAD ANSWER EXAMPLE
- Please refer to these pages.
- You can write code referring these pages.
- Following page will be helpful.

GOOD ANSWER EXAMPLE
- This is sample code:  -- sample code here --
- The answer of you question is -- answer here --

Please make sure to list the URLs of the pages you referenced at the end of your answer. (This will allow users to verify your response.)

Please make sure to answer in the language used by the user. If the user asks in Japanese, please answer in Japanese. If the user asks in Spanish, please answer in Spanish.
But, you can go ahead and search in English, especially for programming-related questions. PLEASE MAKE SURE TO ALWAYS SEARCH IN ENGLISH FOR THOSE.
"""


def init_page():
    st.set_page_config(
        page_title="Web Browsing Agent",
        page_icon="🤗"
    )
    st.header("Web Browsing Agent 🤗")
    st.sidebar.title("Options")
    st.session_state["openai_api_key"] = st.sidebar.text_input(
        "OpenAI API Key", type="password")
    st.session_state["langsmith_api_key"] = st.sidebar.text_input(
        "LangSmith API Key (optional)", type="password")


def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
        ]
        st.session_state.costs = []


def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-4", "GPT-3.5-16k",  "GPT-3.5 (not recommended)"))
    if model == "GPT-4":
        st.session_state.model_name = "gpt-4"
    elif model == "GPT-3.5-16k":
        st.session_state.model_name = "gpt-3.5-turbo-16k"
    elif model == "GPT-3.5 (not recommended)":
        st.session_state.model_name = "gpt-3.5-turbo"
    else:
        raise NotImplementedError
    
    return ChatOpenAI(
        temperature=0,
        openai_api_key=st.session_state["openai_api_key"],
        model_name=st.session_state.model_name,
        streaming=True
    )


def main():
    init_page()
    init_messages()
    tools = [get_search_ddg_tool(), get_fetch_page_tool()]

    """
    This is a sample Web Browsing Agent app that uses LangChain's `OpenAIFunctionsAgent` and Streamlit's `StreamlitCallbackHandler`. Please refer to the code for more details at https://github.com/naotaka1128/web_bowsing_agent.
    """

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if not st.session_state["openai_api_key"]:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        llm = select_model()

    if st.session_state["langsmith_api_key"]:
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
        os.environ['LANGCHAIN_API_KEY'] = st.session_state["langsmith_api_key"]

    if prompt := st.chat_input(placeholder="Who won the 2023 FIFA Women's World Cup?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        search_agent = initialize_agent(
            agent='openai-functions',
            tools=tools,
            llm=llm,
            max_iteration=5,
            agent_kwargs={
                "system_message":  SystemMessage(content=CUSTOM_SYSTEM_PROMPT)
            }
        )
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)

if __name__ == '__main__':
    main()
