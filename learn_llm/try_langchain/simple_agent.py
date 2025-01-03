from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import getpass
import os


# Create the agent
os.environ['TAVILY_API_KEY'] = getpass.getpass("TAVILY ")
model = ChatTongyi(
    model="qwen-turbo",
    temperature=0.8,
    top_p=0.9,
    streaming=False,
    api_key=getpass.getpass("Qwen "),
)

memory = MemorySaver()
search = TavilySearchResults(max_results=1)

tools = [search]
model_with_tool = model.bind_tools(tools=tools)


response = model_with_tool.invoke("英超曼城最近比赛赢了吗？")
print(response)

# Use the agent
agent_executor = create_react_agent(model_with_tool, memory)
results = agent_executor.invoke(
    {"messages": [HumanMessage(content="英超曼城最近比赛赢了吗？")]}
)
print(results)
