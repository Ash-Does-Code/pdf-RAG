from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()

embeddings=OpenAIEmbeddings()

db = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever()


llm = ChatOllama(
    model="llama3.2"
)

while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    # context = "\n\n".join([doc.page_content for doc in docs])

    #asking llm to citations and page numbers

    context = ""

    for doc in docs:
    
                page = doc.metadata["page"] + 1
                context += f"""

                (Page {page})

                {doc.page_content}

                """

    prompt = f"""
    Answer the question using only the context below.
    
    Whenever possible, mention the page number
    where the information came from.

    Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    print("\nAI:", response.content)
    print("-" * 50)
