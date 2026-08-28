from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from database import (
    create_table,
    load_history,
    save_message
)

load_dotenv()
create_table()
chat_history = load_history()

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

# chat_history = [] if using local variable for conv hist

#using inbuilt model's native message format
system = SystemMessage(
    content="""
You are a helpful assistant.

Answer only from the provided context.

Whenever possible, mention page numbers.
"""
)

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

    

    # prompt = f"""
    
    # Conversation History:

    # {history}

    # Context:

    # {context}

    # Current Question:

    # {question}

    # Answer using the context whenever possible.
    # Whenever possible, mention the page number
    # where the information came from.
    # """

    # response = llm.invoke(prompt)

    user_message = HumanMessage(
                    content=f"""
                    Context:

                    {context}

                    Question:

                    {question}
                    """
                    )

    messages = [
    system,
    *chat_history,
    user_message
        ]

    response = llm.invoke(messages)
    
    print("\nAI:", response.content)
    print("-" * 50)

    answer = response.content

    # chat_history.append({
    #        "role":"user",
    #        "content":question
    # })
    # chat_history.append({
    #        "role":"assistant",
    #        "content":response.content
    # })

    chat_history.append(
           HumanMessage(content=question)
    )


    save_message(
        "user",
        question
    )


    chat_history.append(
           AIMessage(content=response.content)
    )

    save_message(
    "assistant",
    response.content
    )

#poitn to note:
# the context is only included in the latest HumanMessage, not in chat_history. That's intentional.
# The retrieved context is specific to the current question and should not be stored as conversation history. 
# Your history should only contain the user's questions and the assistant's answers, while each new question gets fresh context retrieved from the PDF.
# This keeps the conversation clean and avoids repeatedly sending old document chunks back to the model
