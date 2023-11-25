import os

import streamlit as st

# from init import check_an_create_folder, handle_json_file
from init import check_an_create_folder
from init.embedding_utils import embed_documents_in_json_file

# from langchain.document_loaders import TextLoader
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import FAISS


st.header("Cài đặt cho khách hàng")

with st.sidebar.expander("Cài đặt", expanded=True):
    name = st.text_input("Tên chatbot:", key="name_chatbot", value="ChopAI", max_chars=20)
    type_prod = st.text_input("Loại sản phẩm:", key="type_product", value="Thời trang", max_chars=20)
    language = st.selectbox(
        'Ngôn ngữ:',
        ('Tiếng Việt', 'Tiếng Anh'),
        key="langage_product",
        index=0
    )
    ref = st.text_area(
        "Thông tin đính kèm: ",
        height=40, key="info_product",
        value="tên sản phẩm, giá, hình ảnh, đặc biệt phải có link sản phẩm"
    )

if not name or not type_prod or not language or not ref:
    st.info("Vui lòng không bỏ trống thông tin", icon="🚨")
    st.stop()

uploaded_file = st.file_uploader(
    "Vui lòng tải lên danh sách sản phẩm của bạn",
    accept_multiple_files=False,
    type=["json"],
    key="file_uploader",
)
uploaded_business = st.file_uploader(
    "Vui lòng tải lên business cho sản phẩm của bạn",
    accept_multiple_files=False,
    type=["txt"],
    key="file_uploader_bussines"
)

if not uploaded_file or not uploaded_business:
    st.info("Vui lòng nhập đầy đủ thông tin để tiếp tục.", icon="🚨")
    st.stop()

with st.spinner('Đang tải dữ liệu...'):
    check_an_create_folder(os.path.join(os.getcwd(), "resources"))
    file_path = os.path.join(
        os.getcwd(), "resources", uploaded_file.name
    )
    file_path_business = os.path.join(
        os.getcwd(), "resources", 'business_processed.txt'
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        # handle_json_file(file_path, f'{os.path.join(os.getcwd(), "resources")}/data_processed.txt')

    with open(file_path_business, "wb") as f:
        f.write(uploaded_business.getbuffer())

system_message = """
Bạn là một người giới thiệu {0} hữu ích sẽ có cuộc trò chuyện nhẹ nhàng và thân thiện với người dùng để tìm hiểu về
loại {0} mà họ đang tìm kiếm. Luôn tự giới thiệu mình là "{1} người giới thiệu {0}", nhưng thay vì hỏi trực
tiếp về loại {0} họ muốn, hãy có cuộc trò chuyện nhẹ nhàng để hiểu được {0} mà người dùng tìm kiếm. Cố gắng hiểu người dùng
bằng cách nói chuyện với họ về những điều họ cần. Đừng bắt đầu cuộc trò chuyện về {0} như một người bán
hàng. Khi bạn có đủ thông tin, hãy đề xuất một loại {0} cho người dùng. Bạn cũng trả về các JSON
schema như sau, máy chủ có thể trộn lẫn cấu trúc của hai đối tượng JSON, nhưng luôn trả về tất cả các trường của
đối tượng JSON tương ứng:

Luôn luôn trả về Schema sau cho việc truy xuất:

{{
    "your own reasoning": "string", # Giải thích lý do đằng sau đề xuất của bạn.
    "confidence": "string",# Mức độ tin cậy của bạn trong đề xuất, có thể là "low", "medium", hoặc "high".
    "search term for retrieval": "list", # Danh sách các thuật ngữ tìm kiếm chung dựa trên sở thích của người dùng. Chỉ
    trả về nếu độ tin cậy là trung bình hoặc cao. Các thuật ngữ này chỉ nên là tên của {0} và không chứa bất kỳ
    thông tin nào khác. Nếu có nhiều sở thích trong phản hồi của người dùng, trả về danh sách các thuật ngữ tìm kiếm
    khác nhau cho mỗi sở thích. Luôn bao gồm tất cả các khía cạnh của sở thích của người dùng như một thuật ngữ tìm
    kiếm riêng biệt. Chỉ bao gồm càng nhiều thuật ngữ cần thiết.
    "your response to user": "string" # Phản hồi của bạn đến người dùng, đây là điều người dùng sẽ thấy. Luôn đính 
    kèm các thông tin quan trọng như {3} v.v. Nếu có nhiều sản phẩm phù hợp, hãy đề xuất nhiều sản phẩm. Nếu bạn không 
    có sản phẩm phù hợp, hãy đề xuất một loại {0} cho người dùng (nhiều nhất là 3 sản phẩm).
}}
LƯU Ý:
Chỉ trả về tên "search term for retrieval" phù hợp với sở thích của người dùng trong lĩnh vực {0} khi bạn có đủ tự tin.

Đừng trả lại một hỗn hợp của các đối tượng JSON. Chỉ trả lại một hoặc một loại khác.

Nếu "confidence" là "low" thì phải trả về "search term for retrieval" là danh sách rỗng.

Luôn nói chuyện bằng ngôn ngữ {2}.

Luôn trả về "your response to use" dưới dạng markdown.
""".format(type_prod, name, language, ref)

# st.markdown(system_message)
if st.button("Tạo chatbot"):
    with st.spinner('Đang tải thông tin và tạo chatbot...'):
        with open(os.path.join(os.getcwd(), 'resources/system_message'), 'w') as file:
            file.write(system_message)

        output_file_path = os.path.join(os.getcwd(), "resources/processed_data_with_embeddings.json")
        embed_documents_in_json_file(file_path, output_file_path)

        # loader = TextLoader(
        #     file_path=os.path.join(os.getcwd(), "resources/data_processed.txt"),
        #     encoding="utf-8",
        # )
        # data = loader.load_and_split(
        #     text_splitter=RecursiveCharacterTextSplitter(
        #         chunk_size=4000,
        #         chunk_overlap=4,
        #     ), )
        #
        # db = FAISS.from_documents(
        #     data,
        #     OpenAIEmbeddings(),
        # )
        # db.save_local(os.path.join(os.getcwd(), 'resources/vectordb'))
        st.success("Tạo chatbot thành công")
