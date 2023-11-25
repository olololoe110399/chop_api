import os

import streamlit as st
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from app.init.llm2 import Recommender
from init import check_an_create_folder, handle_json_file

st.header(":rocket: Trò chuyện với ChopAI :page_facing_up:")
st.write("Định dạng file hỗ trợ: JSON :city_sunrise:")

# llm = LLM()

with st.sidebar.expander("Settings", expanded=True):
    uploaded_file = st.file_uploader("Vui lòng tải lên danh sách sản phẩm của bạn", accept_multiple_files=False,
                                     type=None)
    if uploaded_file and "vectorstore" not in st.session_state and "client" not in st.session_state:
        with st.spinner('Đang tải dữ liệu...'):
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
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                data = loader.load_and_split(text_splitter=RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=0,
                ))
                embeddings = OpenAIEmbeddings()
                vectorstore = FAISS.from_documents(data, embeddings)

                st.session_state['vectorstore'] = vectorstore
                st.session_state['recommender'] = Recommender()
                st.success(f"Đã xử lý xong file {uploaded_file.name}")

if not uploaded_file:
    st.info("Vui lòng tải lên danh sách sản phẩm của bạn để tiếp tục.", icon="🚨")
    st.stop()


def markdown_realtime(text):
    st.markdown(text)


if "recommender" in st.session_state:
    vectorstore = st.session_state['vectorstore']
    recommender = st.session_state['recommender']

    if "messages" not in st.session_state:
        with open("app/resources/system_message", "r") as file:
            system_message = file.read()
        st.session_state.messages = [{
            "role": "system",
            "content": system_message
        }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask your questions?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner('Đang suy nghĩ  ...'):
                    recommender_response = recommender.recommend("user", prompt)
                if 'search term for retrieval' not in recommender_response:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": recommender_response['your response to user']}
                    )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()

                if len(recommender_response['search term for retrieval']) == 0:
                    st.session_state.messages.append({"role": "assistant",
                                                      "content": recommender_response['your response to user']}
                                                     )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()

                results = vectorstore.similarity_search(
                    ", ".join(recommender_response['search term for retrieval']))
                if len(results) == 0:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": recommender_response['your response to user']
                    })
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                retrievals = []
                for result in results[:3]:
                    retrievals.append(result.page_content)
                if len(retrievals) == 0:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": recommender_response['your response to user']
                    })
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                with st.spinner('Đang gợi ý  ...'):
                    final_result = recommender.recommend(
                        "assistant",
                        f"Đây là trang phục phù hợp với người dùng hãy:\n\n {retrievals}"
                        f"hãy ghi nhớ những đề xuất này trong suốt cuộc trò chuyện "
                        f"của bạn với người dùng và bây giờ hãy gợi ý sản phẩm phù hợp hơn cho người dùng. "
                        f"(Luôn luôn đính kèm sản phẩm)",
                    )
                    st.markdown(final_result['your response to user'])
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": final_result['your response to user']}
                    )
            except Exception as e:
                print(e)
                st.error("Có lỗi xảy ra, vui lòng thử lại.")
                st.stop()
