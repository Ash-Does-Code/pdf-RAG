import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


load_dotenv()

loader=PyPDFLoader('')
documents=loader.load()
splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)
chunks=splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()

db=FAISS.from_documents(chunks,embeddings)

db.save_local("vectorstore")

