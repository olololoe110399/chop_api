from abc import ABC

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler


class PrintRetrievalHandler(BaseCallbackHandler, ABC):
    def __init__(self, container: st.delta_generator.DeltaGenerator):
        self.status = container.status("**Context Retrieval**")

    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        self.status.write(f"**Question:** {query}")
        self.status.update(label=f"**Thinking...**")

    def on_retriever_end(self, documents, **kwargs):
        self.status.update(state="complete", label=f"**Complete**")
