import os

import streamlit as st

from init.llm2 import Recommender
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
from init.similarity_search import SimilaritySearch

st.header(":rocket: Trò chuyện với ChopAI :page_facing_up:")

st.sidebar.info("Vui lòng reload lại trang sau khi cài đặt của khách hàng.", icon="🚨")

try:

    if "vectorstore" not in st.session_state:
        with st.spinner('Đang tải dữ liệu...'):
            # if not os.path.exists(os.path.join(os.getcwd(), 'resources/vectordb')):
            if not os.path.exists(os.path.join(os.getcwd(), 'resources/processed_data_with_embeddings.json')):
                st.info("Vui lòng tạo chatbot trước khi sử dụng.", icon="🚨")
                st.stop()
            vectorstore = SimilaritySearch(os.path.join(os.getcwd(), 'resources/processed_data_with_embeddings.json'))
            # vectorstore = FAISS.load_local(os.path.join(os.getcwd(), 'resources/vectordb'), OpenAIEmbeddings())
            st.session_state['vectorstore'] = vectorstore

    if "vectorstore" in st.session_state:
        vectorstore = st.session_state['vectorstore']

        if "messages" not in st.session_state:
            with open(os.path.join(os.getcwd(), "resources/system_message"), "r") as file:
                system_message = file.read()
            st.session_state.messages = [{
                "role": "system",
                "content": system_message
            }]
            recommender = Recommender()
            st.session_state['recommender'] = recommender

        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask your questions?"):
            recommender = st.session_state['recommender']
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner('Đang suy nghĩ  ...'):
                    recommender_response = recommender.recommend(
                        "user",
                        f"""Tư vấn và chăm sóc khách hàng  đây là câu hỏi của KH hàng: {prompt}"""
                    )
                if 'search term for retrieval' not in recommender_response:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": recommender_response['your response to user']}
                    )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                if len(recommender_response['search term for retrieval']) == 0:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": recommender_response['your response to user']}
                    )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                results = vectorstore.similarity_search(
                    recommender_response['search term for retrieval'][:3],
                )

                if len(results) == 0:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": recommender_response['your response to user']}
                    )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                retrievals = []
                for result in results[:3]:
                    for record in result.head(3).to_dict('records'):
                        record.pop('embeddings', None)
                        record.pop('similarities', None)
                        retrievals.append(record)

                if len(retrievals) == 0:
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": recommender_response['your response to user']
                        }
                    )
                    st.markdown(recommender_response['your response to user'])
                    st.stop()
                print("retrievals", retrievals)
                with st.spinner('Đang gợi ý  ...'):
                    final_result = recommender.recommend(
                        "assistant",
                        f"Đây là các sản phẩm phù hợp với người dùng: \n\n {str(retrievals)}"
                        f"Hãy ghi nhớ những đề xuất này trong suốt cuộc trò chuyện "
                        f"của bạn với người dùng và bây giờ hãy trả lời cho người dùng thông tin của sản phẩm này "
                        f"và nhớ tư vấn vì sao nên dùng những sản phẩm này."
                        f"(Luôn luôn đính kèm url, image_url, name, price một cách đẹp mắt bằng markdown nếu có)"
                        f"LƯU Ý: Không được tự tạo sản phẩm giả, chỉ trả về các sản phẩm từ phù hợp ở trên"
                    )
                    st.markdown(final_result['your response to user'])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_result['your response to user']
                    })
except Exception as e:
    st.error(e)
    st.error("Có lỗi xảy ra, vui lòng thử lại.")
