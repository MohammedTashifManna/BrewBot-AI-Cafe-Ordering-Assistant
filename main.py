import streamlit as st
import time
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from collections.abc import Iterable
from random import randint
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import tool

load_dotenv()

st.title("☕ BrewBot")

#########################################
# CONFIG
#########################################

WELCOME_MSG = "Welcome to Brew Signature Cafe☕. How may I serve you today?"

BREWBOT_SYSINT = (
    "system",
    """
You are BrewBot, an interactive cafe ordering system for Brew Signature Cafe.

Rules:
- If user asks menu/items/drinks → ALWAYS call get_menu
- Add drinks using add_to_order
- Use get_order if needed
- Always confirm before place_order
- Only use items from menu
- Thank user after order is placed
- No other topics to be discussed
"""
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

#########################################
# SESSION STATE
#########################################

if "history" not in st.session_state:
    st.session_state.history = [{"role":"assistant","content":WELCOME_MSG}]

if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "messages":[],
        "order":[],
        "finished":False
    }

#########################################
# STREAM EFFECT
#########################################

def chat_stream(text):
    for char in text:
        yield char
        time.sleep(.01)

#########################################
# STATE
#########################################

class OrderState(TypedDict):
    messages: Annotated[list, add_messages]
    order:list[str]
    finished:bool

#########################################
# TOOLS
#########################################

@tool
def get_menu()->str:
    """Get cafe menu"""

    return """
MENU ☕

Coffee:
- Espresso
- Americano
- Cold Brew
- Latte
- Cappuccino
- Mocha
- Flat White

Tea:
- Green Tea
- Earl Grey
- Chai Latte
- Matcha Latte

Other:
- Hot Chocolate

Modifiers:
Milk:
- Whole
- Oat
- Almond

Shots:
- Single
- Double
- Triple

Temperature:
- Hot
- Iced
"""


@tool
def add_to_order(
        drink:str,
        modifiers:Iterable[str]
)->str:
    """Add drink"""


@tool
def get_order()->str:
    """Get current order"""


@tool
def confirm_order()->str:
    """Confirm order"""


@tool
def clear_order():
    """Clear order"""


@tool
def place_order()->int:
    """Place order"""


#########################################
# LLM + TOOLS
#########################################

auto_tools=[get_menu]

order_tools=[
    add_to_order,
    get_order,
    confirm_order,
    clear_order,
    place_order
]

tool_node=ToolNode(auto_tools)

llm_with_tools=llm.bind_tools(
    auto_tools+order_tools
)

#########################################
# CHATBOT NODE
#########################################

def chatbot(state:OrderState):
    defaults={
        "order":[],
        "finished":False
    }
    response=llm_with_tools.invoke(
        [BREWBOT_SYSINT]
        +state["messages"]
    )
    return defaults | state | {
        "messages":[response]
    }

#########################################
# ROUTING
#########################################

def route_tools(state):
    msg=state["messages"][-1]
    if state["finished"]:
        return END

    if hasattr(msg,"tool_calls"):
        if len(msg.tool_calls)>0:
            if any(
                tool["name"]
                in tool_node.tools_by_name
                for tool in msg.tool_calls
            ):
                return "tools"
            return "ordering"
    return END

#########################################
# ORDER NODE
#########################################

def ordering_node(state):

    tool_msg=state["messages"][-1]
    order=state["order"]
    outbound=[]
    order_placed=False

    for tool_call in tool_msg.tool_calls:
        name=tool_call["name"]
        if name=="add_to_order":
            drink=tool_call["args"]["drink"]
            modifiers=tool_call["args"]["modifiers"]
            mod_str=", ".join(modifiers)
            order.append(f"{drink} ({mod_str})")
            response="\n".join(order)

        elif name=="get_order":
            response="\n".join(order)

        elif name=="confirm_order":
            response=("Current Order:\n"+"\n".join(order))

        elif name=="clear_order":
            order.clear()
            response="Order cleared"

        elif name=="place_order":
            mins=randint(5,10)
            response=(
                f"Order sent!\n"
                f"ETA: {mins} mins"
            )
            order_placed=True

        else:
            response="Unknown action"

        outbound.append(
            ToolMessage(
                content=response,
                name=name,
                tool_call_id=tool_call["id"]
            )
        )

    return {
        "messages":outbound,
        "order":order,
        "finished":order_placed
    }


#########################################
# GRAPH
#########################################

builder=StateGraph(OrderState)
builder.add_node("chatbot",chatbot)
builder.add_node("tools",tool_node)
builder.add_node("ordering",ordering_node)
builder.add_edge(START,"chatbot")
builder.add_conditional_edges("chatbot",route_tools)
builder.add_edge("tools","chatbot")
builder.add_edge("ordering","chatbot")
graph=builder.compile()
config={"recursion_limit":100}

#########################################
# SHOW HISTORY
#########################################

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

#########################################
# USER INPUT
#########################################

prompt=st.chat_input("Type here...")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.history.append({"role":"user", "content":prompt})
    st.session_state.graph_state["messages"].append( ("user",prompt))
    result=graph.invoke(st.session_state.graph_state,config )
    st.session_state.graph_state=result
    response=result["messages"][-1].content

    with st.chat_message("assistant"):
        streamed=st.write_stream(chat_stream(response))

    st.session_state.history.append({"role":"assistant","content":streamed})
