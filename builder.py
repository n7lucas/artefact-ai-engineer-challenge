from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes.chatbot import create_chatbot_node
from tools import create_emporio_tools

def build_emporio_agent(checkpointer: MemorySaver = None):
    """Monta a máquina de estados declarativa do agente no LangGraph com ciclo ReAct e persistência de sessão."""
    tools = create_emporio_tools()
    
    workflow = StateGraph(AgentState)

    # 1. Adição dos Nós
    workflow.add_node("chatbot", create_chatbot_node(tools))
    workflow.add_node("tools", ToolNode(tools))

    # 2. Definição do Fluxo ReAct
    workflow.add_edge(START, "chatbot")

    # Transição condicional: Se o LLM gerar tool_calls, vai para 'tools'. Caso contrário, devolve a resposta final
    workflow.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    
    # Após a execução da ferramenta, retorna obrigatoriamente ao nó 'chatbot' para síntese da resposta
    workflow.add_edge("tools", "chatbot")

    # 3. Compilação com Checkpointer para Memória de Sessão
    memory = checkpointer if checkpointer is not None else MemorySaver()
    return workflow.compile(checkpointer=memory)