import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from vectorstore.chroma_store import get_vectorstore
from db.chat_store import get_user_history

# Initialize core components once
vectorstore = get_vectorstore()

# Pre-warm vector store to avoid cold start latency
print("🔥 Warming up vector store...")
try:
    vectorstore.similarity_search("warmup", k=1)
    print("✅ Vector store ready!")
except Exception as e:
    print(f"⚠️  Warmup query failed: {e}")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# Create the prompt template
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
    """Add a new document's content to the vector store."""
    text = content.decode("utf-8", errors="ignore")
    metadata = {"user": user_email, "filename": filename}
    vectorstore.add_texts(texts=[text], metadatas=[metadata])

def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join([doc.page_content for doc in docs])

def format_chat_history(history):
    """Convert chat history tuples to LangChain message objects."""
    messages = []
    for question, answer in history:
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=answer))
    return messages

def process_query(user_email, query):
    """Retrieve relevant context and generate an AI response."""
    # Track timing for different stages
    timings = {}

    # Load chat history for context
    start_time = time.time()
    chat_history = get_user_history(user_email)
    formatted_history = format_chat_history(chat_history)
    timings['history_time'] = time.time() - start_time

    # Create retriever (k=2 for faster retrieval with minimal quality loss)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # Get relevant documents
    start_time = time.time()
    docs = retriever.invoke(query)
    context = format_docs(docs)
    timings['retrieval_time'] = time.time() - start_time

    # Create the chain using LCEL
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

    # Get the answer (this is where OpenAI API is called)
    start_time = time.time()
    answer = chain.invoke(query)
    timings['llm_time'] = time.time() - start_time

    return answer, docs, timings
