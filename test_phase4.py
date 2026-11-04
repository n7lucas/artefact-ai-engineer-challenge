from langchain_core.messages import HumanMessage
from builder import build_emporio_agent

def main():
    print("=== TESTANDO FASE 4: AGENTE LANGGRAPH COM PERSONA E MEMÓRIA ===")
    
    app = build_emporio_agent()
    
    # Configuração da sessão do cliente (thread_id)
    config = {"configurable": {"thread_id": "sessao_cliente_001"}}

    # Teste 1: Consulta de catálogo (Violões de nylon até R$ 800)
    print("\n--- Teste 1: Consulta de Catálogo (Violões de nylon até R$ 800) ---")
    msg1 = HumanMessage(content="Quais opções de violões de nylon disponíveis vocês têm custando até 800 reais?")
    for event in app.stream({"messages": [msg1]}, config, stream_mode="values"):
        last_msg = event["messages"][-1]
    print(f"\n[AGENTE]:\n{last_msg.content}")

    # Teste 2: Pergunta fora do escopo (Recusa educada de acessórios)
    print("\n--- Teste 2: Pergunta Fora do Escopo (Acessórios) ---")
    msg2 = HumanMessage(content="Vocês vendem palhetas e encordoamento de aço para violão?")
    for event in app.stream({"messages": [msg2]}, config, stream_mode="values"):
        last_msg = event["messages"][-1]
    print(f"\n[AGENTE]:\n{last_msg.content}")

    # Teste 3: Consulta de Políticas (Direito de Arrependimento)
    print("\n--- Teste 3: Consulta de Políticas (Devolução) ---")
    msg3 = HumanMessage(content="Se eu comprar um violão pelo site e me arrepender, como funciona a devolução?")
    for event in app.stream({"messages": [msg3]}, config, stream_mode="values"):
        last_msg = event["messages"][-1]
    print(f"\n[AGENTE]:\n{last_msg.content}")

if __name__ == "__main__":
    main()