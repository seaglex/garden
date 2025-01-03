from langchain_community.chat_models.tongyi import ChatTongyi
from typing import Annotated, List, Any
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from typing_extensions import TypedDict
from typing import List, Optional, Literal
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command, Send
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

import getpass
import os


llm = ChatTongyi(
    model="qwen-turbo",
    temperature=0.8,
    top_p=0.9,
    streaming=False,
    api_key=getpass.getpass("Qwen "),
)


@tool
def mock_search_tool(query: str) -> Any:
    """Internal search engine"""
    mock_msg = [{
        "url": "https://baijiahao.baidu.com/s?id=1819899487398931179",
        "title": "2-0！英超卫冕冠军大爆发，2024收官战曼城赢了，两亿巨星破球荒",
        "content": "Dec 30, 2024 曼城在2024年的最后一场比赛中2比0干净利落地拿下了莱斯特城。",
        "score": "0.8",
        "raw_content": None,
    }]
    return mock_msg


@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )


# nodes
def make_supervisor_node(llm: BaseChatModel, members: list[str]) -> str:
    options = ["FINISH"] + members
    system_prompt = (
"""# 角色
你是一位高效的对话管理专家，负责协调和管理以下工作人员：[search, web_scraper]。你的任务是根据用户请求，决定下一步由哪个工作人员执行任务。每个工作人员将执行其任务并返回结果和状态。当所有任务完成后，回复“FINISH”。

## 技能
### 技能1: 任务分配
- 根据用户请求，确定需要执行的任务。"""
f"- 分配任务给合适的工作人员{members}。"
""""- 确保任务分配合理，以提高工作效率。

### 技能2: 结果收集与处理
- 收集工作人员返回的结果和状态。
- 根据结果和状态决定下一步行动。
- 如果任务完成，回复“FINISH”。

## 限制
- 只处理与任务分配和结果收集相关的工作。
- 不直接参与具体任务的执行，仅负责管理和协调。
- 在所有任务完成后，必须回复“FINISH”以结束对话。
- 只能回复search 或 web_scraper 或 FINISH"""
    )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""

        next: Literal[*options]

    def supervisor_node(state: MessagesState) -> Command[Literal[*members, "__end__"]]:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto)

    return supervisor_node


def make_tavily_agent():
    os.environ['TAVILY_API_KEY'] = getpass.getpass("TAVILY ")
    tavily_tool = TavilySearchResults(max_results=2)
    search_agent = create_react_agent(llm, tools=[tavily_tool])
    return search_agent


def make_mock_search_agent():
    class MockSearchAgent:
        def invoke(self, state: MessagesState):
            msg = HumanMessage(content="据搜索所知，2024年12月30日，曼城终于战胜莱斯特城，结束五场不胜")
            return {"messages": [msg]}

    return MockSearchAgent()


search_agent = make_mock_search_agent()
def search_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = search_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="search")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])
def web_scraper_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = web_scraper_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_scraper")
            ]
        },
        # We want our workers to ALWAYS "report back" to the supervisor when done
        goto="supervisor",
    )


research_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"])

research_builder = StateGraph(MessagesState)
research_builder.add_node("supervisor", research_supervisor_node)
research_builder.add_node("search", search_node)
research_builder.add_node("web_scraper", web_scraper_node)

research_builder.add_edge(START, "supervisor")
research_graph = research_builder.compile()

for s in research_graph.stream(
    {"messages": [("user", "曼城2024年最后一场胜利赢了谁？")]},
    {"recursion_limit": 5},
):
    print(s)
    print("---")
