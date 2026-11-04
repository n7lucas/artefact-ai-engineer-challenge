import os
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

def build_policy_vectorstore(pdf_path: str = settings.pdf_path):
    """Read the store policies PDF and create a FAISS vector search index.."""
    if not os.path.exists("data//" + pdf_path):
        raise FileNotFoundError(f"Arquivo PDF de políticas não encontrado em: {"data//" + pdf_path}")

    reader = PdfReader("data//" + pdf_path)
    raw_documents = []

    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_documents.append(
                Document(
                    page_content=text,
                    metadata={"page": idx + 1, "source": os.path.basename(pdf_path)}
                )
            )

    # Chunking for 8 pages
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(raw_documents)
    
    # Using HuggingFace Free Embedder model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    
    print(f"✅ RAG Vetorial criado: {len(split_docs)} chunks indexados a partir de {len(raw_documents)} páginas.")
    return vectorstore.as_retriever(search_kwargs={"k": 2})