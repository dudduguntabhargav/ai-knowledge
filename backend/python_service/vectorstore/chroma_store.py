import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Create embedding model using OpenAI API key
def get_vectorstore():
    persist_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(persist_dir, exist_ok=True)

    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    store = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    return store
