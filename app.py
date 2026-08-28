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

chat_history = []

while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)

    #normal context
    # context = "\n\n".join([doc.page_content for doc in docs])
    #asking llm to citations and page numbers

    context = ""

    for doc in docs:
    
                page = doc.metadata["page"] + 1
                context += f"""

                (Page {page})

                {doc.page_content}

                """
    #simple page number and citations
    # prompt = f"""
    # Answer the question using only the context below.

    # Whenever possible, mention the page number
    # where the information came from.

    # Context:
    # {context}

    # Question:
    # {question}
    # """
    
    history = "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in chat_history
    )

    prompt = f"""
    
    Conversation History:

    {history}

    Context:

    {context}

    Current Question:

    {question}

    Answer using the context whenever possible.
    Whenever possible, mention the page number
    where the information came from.
    """

    response = llm.invoke(prompt)

    print("\nAI:", response.content)
    print("-" * 50)

    answer = response.content

    chat_history.append({
           "role":"user",
           "content":question
    })
    chat_history.append({
           "role":"assistant",
           "content":response.content
    })
    chat_history = chat_history[-6:]
