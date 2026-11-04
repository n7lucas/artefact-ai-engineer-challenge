from llm import get_resilient_llm
from tools import create_emporio_tools
from langchain_core.messages import SystemMessage, HumanMessage

def main():
    print("=== TESTANDO FASE 3: LLM RESILIENTE & LANGSMITH ===")
    
    # 1. Carrega as ferramentas e a LLM resiliente
    tools = create_emporio_tools()
    llm = get_resilient_llm().bind_tools(tools)

    # 2. Teste de invocação simples
    prompt = [
        SystemMessage(content="Você é o assistente virtual da Empório da Música."),
        HumanMessage(content="Quais são as ferramentas disponíveis para você consultar dados?")
    ]

    print("\n--- Testando invocação direta do modelo ---")
    response = llm.invoke(prompt)
    print(f"Resposta do modelo:\n{response.content}")

    # 3. Teste de intenção de Tool Calling
    prompt_tool = [
        SystemMessage(content="Você é o assistente virtual da Empório da Música."),
        HumanMessage(content="Quanto custa o violão Yamaha C40?")
    ]

    print("\n--- Testando intenção de chamada de ferramenta (Tool Calling) ---")
    response_tool = llm.invoke(prompt_tool)
    
    if response_tool.tool_calls:
        print(f"✅ Chamada de Tool identificada com sucesso: {response_tool.tool_calls}")
    else:
        print(f"Resposta direta: {response_tool.content}")

if __name__ == "__main__":
    main()

    