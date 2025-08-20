from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings
from app.services.document_service import vectorstore

# This is the full, correct content of the file.
# The lines that caused the SyntaxError have been removed.

llm = ChatOllama(model="phi", base_url=settings.OLLAMA_BASE_URL)
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def query_rag_pipeline(query: str):
    response = rag_chain.invoke(query)
    source_documents = retriever.get_relevant_documents(query)
    return {
        "response": response,
        "source_documents": [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in source_documents
        ]
    }