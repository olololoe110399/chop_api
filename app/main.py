from langchain.document_loaders import TextLoader
from rich.console import Console

from init.llm import LLM

console = Console()

if __name__ == '__main__':
    llm = LLM()
    loader = TextLoader(
        file_path="app/resources/data_processed.txt",
        encoding="utf-8",
    )

    data = loader.load()
    conversation_retrieval_chain = llm.init_conversation_retrieval_chain(data)
    conversation_chain = llm.init_conversation_chain()
    histories = []
    while True:
        input = console.input("Enter your question: ")
        output = conversation_retrieval_chain(
            inputs={
                "question": input,
                "chat_history": histories
            },
            return_only_outputs=True,
        )
        histories.append(output['answer'])
