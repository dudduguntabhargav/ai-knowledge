import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from vectorstore.chroma_store import get_vectorstore
from db.chat_store import get_user_history, get_active_document, get_user_documents, track_document_upload, save_chat
from utils.document_processor import extract_text_from_file, chunk_text

vectorstore = get_vectorstore()

print("Warming up vector store...")
try:
    vectorstore.similarity_search("warmup", k=1)
    print("Vector store ready!")
except Exception as e:
    print(f"Warmup query failed: {e}")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. You have access to documents uploaded by the user.

Use the following context from the user's uploaded documents to answer their question. The context below contains relevant excerpts from their documents:

Context:
{context}

Instructions:
- Answer based on the information in the context above
- If the context contains the answer, provide it clearly and concisely
- If asked for a summary, summarize the content from the context
- If the context doesn't contain enough information, say so
- Be direct and helpful"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

def store_document(user_email, content, filename):
    text, file_type = extract_text_from_file(content, filename)

    chunks = chunk_text(text, chunk_size=1000, overlap=200)

    metadatas = [
        {
            "user": user_email,
            "filename": filename,
            "file_type": file_type,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        for i in range(len(chunks))
    ]

    vectorstore.add_texts(texts=chunks, metadatas=metadatas)

    track_document_upload(user_email, filename, file_type)

    print(f"✅ Stored {len(chunks)} chunks from {filename} ({file_type})")
    return filename

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def format_chat_history(history):
    messages = []
    for question, answer in history:
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=answer))
    return messages

def detect_document_in_query(query, user_documents):
    query_lower = query.lower()
    for doc_name in user_documents:
        doc_base = doc_name.rsplit('.', 1)[0].lower()
        if doc_base in query_lower or doc_name.lower() in query_lower:
            return doc_name
    return None

def process_query(user_email, query, document_filter=None):
    timings = {}

    start_time = time.time()
    formatted_history = []
    timings['history_time'] = time.time() - start_time

    start_time = time.time()
    user_documents = get_user_documents(user_email)

    document_to_use = (
        document_filter or
        detect_document_in_query(query, user_documents) or
        get_active_document(user_email)
    )

    print(f"🔍 Using document: {document_to_use} (filter={document_filter}, active={get_active_document(user_email)})")

    search_kwargs = {"k": 3}

    if document_to_use:
        search_kwargs["filter"] = {
            "$and": [
                {"filename": document_to_use},
                {"user": user_email}
            ]
        }
    else:
        search_kwargs["filter"] = {"user": user_email}

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    timings['context_setup'] = time.time() - start_time

    start_time = time.time()
    docs = retriever.invoke(query)
    context = format_docs(docs)
    timings['retrieval_time'] = time.time() - start_time

    chain = (
        {
            "context": lambda x: context,
            "chat_history": lambda x: formatted_history,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    start_time = time.time()
    answer = chain.invoke(query)
    timings['llm_time'] = time.time() - start_time

    return answer, docs, timings, document_to_use

def process_query_stream(user_email, query, document_filter=None):
    user_documents = get_user_documents(user_email)

    document_to_use = (
        document_filter or
        detect_document_in_query(query, user_documents) or
        get_active_document(user_email)
    )

    print(f"🔍 [STREAM] Using document: {document_to_use}")

    search_kwargs = {"k": 3}

    if document_to_use:
        search_kwargs["filter"] = {
            "$and": [
                {"filename": document_to_use},
                {"user": user_email}
            ]
        }
    else:
        search_kwargs["filter"] = {"user": user_email}

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    docs = retriever.invoke(query)
    context = format_docs(docs)
    formatted_history = []

    chain = (
        {
            "context": lambda x: context,
            "chat_history": lambda x: formatted_history,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    full_response = ""
    for chunk in chain.stream(query):
        if chunk:
            full_response += chunk
            yield chunk

    source_docs = [{"filename": doc.metadata.get("filename"), "page": doc.metadata.get("chunk_index")} for doc in docs]
    save_chat(user_email, query, full_response, document_name=document_to_use, sources=source_docs)
