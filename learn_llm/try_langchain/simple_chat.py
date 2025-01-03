from langchain_community.chat_models.tongyi import ChatTongyi
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

model = ChatTongyi(
    model="qwen-turbo",
    temperature=0.8,
    top_p=0.9,
    streaming=False,
    api_key=getpass.getpass(),
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a good servant. Answer all questions to the best of your ability."),
    MessagesPlaceholder(variable_name="messages")]
)
def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

while True:
    query = input("Input uid#query ")
    if query=="exit":
        break
    uid, query = query.split("#")
    config = {"configurable": {"thread_id": uid}}
    input_messages = [query]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()
