import os

import streamlit as st
from langchain.document_loaders import TextLoader
from init.llm import LLM
from init import check_an_create_folder, handle_json_file
from init.print_retrieval_handler import PrintRetrievalHandler
from init.stream_handler import StreamHandler

st.header(":rocket: Trò chuyện với ChopAI :page_facing_up:")
st.write("Định dạng file hỗ trợ: JSON :city_sunrise:")

llm = LLM()

with st.sidebar.expander("Settings", expanded=True):
    uploaded_file = st.file_uploader("Vui lòng tải lên danh sách sản phẩm của bạn", accept_multiple_files=False,
                                     type=None)
    if uploaded_file:
        with st.spinner('Đang tải đang dữ liệu...'):
            file_path = os.path.join(
                os.getcwd(), "app/resources", uploaded_file.name
            )
            check_an_create_folder(os.path.join(os.getcwd(), "app/resources"))
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                handle_json_file(file_path, f'{os.path.join(os.getcwd(), "app/resources")}/data_processed.txt')
                loader = TextLoader(
                    file_path="app/resources/data_processed.txt",
                    encoding="utf-8",
                )

                data = loader.load()
                conversation_retrieval_chain = llm.init_conversation_retrieval_chain(data)
                # conversation_chain = llm.init_conversation_chain()
                st.session_state['conversation_retrieval_chain'] = conversation_retrieval_chain
                st.success(f"Đã xử lý xong file {uploaded_file.name}")

if not uploaded_file:
    st.info("Vui lòng tải lên danh sách sản phẩm của bạn để tiếp tục.", icon="🚨")
    st.stop()

if not data:
    st.info("Đã có lỗi xảy ra, vui lòng thử lại.", icon="🚨")
    st.stop()

if "conversation_retrieval_chain" in st.session_state:
    conversation_retrieval_chain = st.session_state['conversation_retrieval_chain']

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your questions?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            retrieval_handler = PrintRetrievalHandler(st.container())
            stream_handler = StreamHandler(st.empty())
            result = conversation_retrieval_chain({
                "question": prompt,
                "chat_history": [
                    (message["role"], message["content"]) for message in
                    st.session_state.messages
                ],
            }, callbacks=[retrieval_handler, stream_handler])
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})