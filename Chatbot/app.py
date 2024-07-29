
import logging
import streamlit as st
import uuid
import bedrock

# define logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger.info("Logging Started")


# streamlit app here
User_icon = "images/User_icon.png"
bot_icon ="images/AI_icon.png"

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
else:
    user_id = str(uuid.uuid4())
    st.session_state["user_id"] = user_id

if "llm_chain" not in st.session_state:
    st.session_state["llm_app"] = bedrock
    st.session_state["llm_chain"] = bedrock.bedrock_chain()

if "questions" not  in st.session_state:
    st.session_state.questions =[]

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input =""


def Create_topbar():
    col1, col2, col3 = st.columns([2,10,3])
    with col2:
        header = "Amazon Bedrock chatbot App"
        st.write(f"<h3 class='main-header'>{header}</h3>",unsafe_allow_html=True)
    with col3:
        clear = st.button("Clear chat")
    return clear
clear = Create_topbar()

if clear:
    st.session_state.questions =[]
    st.session_state.answers =[]
    st.session_state.input =""
    bedrock.clear_memory(st.session_state["llm_chain"])

def handle_input():
    input = st.session_state.input

    llm_chain = st.session_state["llm_chain"]
    chain = st.session_state["llm_app"]
    result,amount_of_tokens = chain.run_chain(llm_chain,input)
    question_with_id ={
        "question":input,
        "id":len(st.session_state.questions),
        "tokens":amount_of_tokens
    }
    st.session_state.questions.append(question_with_id)
    st.session_state.answers.append({"answer":result,"id":len(st.session_state.questions)})
    st.session_state.input =""

def write_user_message(md):
    col1, col2 =st.columns([1,12])

    with col1:
        st.image(User_icon, use_column_width="always")
    with col2:
        st.warning(md["question"])
        st.write(f"Tokens used:{md['tokens']}")

def render_answer(ans):
    col1, col2 = st.columns([1,12])
    with col1:
        st.image(bot_icon, use_column_width="always")
    with col2:
        st.info(ans["response"])

def write_chat_message(md):
    chat = st.container()
    with chat:
        render_answer(md["answer"])

with st.container():
    for q, a in zip(st.session_state.questions, st.session_state.answers):
        write_user_message(q)
        write_chat_message(a)

st.markdown("-----")
input = st.text_input(
    "you are takling to a AI, ask any question",
    key="input",
    on_change=handle_input
)