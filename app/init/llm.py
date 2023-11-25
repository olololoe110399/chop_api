from typing import List

from langchain.chains import ConversationalRetrievalChain, ConversationChain
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate
from langchain.vectorstores import FAISS

from app.logger.logger import custom_logger


class LLM:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            temperature=0,
            max_tokens=4000,
            model_name="gpt-3.5-turbo-16k",
            streaming=True,
        )
        self.conversation_memory = ConversationBufferMemory(
            return_messages=True,
            memory_key='chat_history',
            input_key='question',
        )
        with open("app/resources/system_message.txt", "r") as file:
            self.system_message = file.read()

    def init_conversation_retrieval_chain(self, data: List[Document]) -> BaseConversationalRetrievalChain:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(data, embeddings)
        custom_logger.info("Creating a vectorstore")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_message),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(),
            verbose=True,
            memory=self.conversation_memory,
            condense_question_prompt=prompt
        )
        custom_logger.info(f'conversation_retrieval_chain')
        return chain

    def init_conversation_chain(self) -> ConversationChain:
        chain = ConversationChain(
            llm=self.llm,
            verbose=True,
            # memory=self.conversation_memory
        )
        custom_logger.info(f'conversation_chain')
        return chain
