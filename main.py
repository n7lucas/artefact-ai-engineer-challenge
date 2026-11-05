import sys
import uuid
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from builder import build_emporio_agent

def run_cli():
    print("=" * 65)
    print("🎸 EMPÓRIO DA MÚSICA - ASSISTENTE VIRTUAL DE ATENDIMENTO")
    print("=" * 65)
    print("Digite a sua pergunta ou 'sair' para encerrar a conversa.\n")

    # Inicializa o agente compilado
    app = build_emporio_agent()
    
    # Gera um ID de sessão único para a execução do terminal
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            user_input = input("\n👤 Cliente: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n🤖 Assistente: Muito obrigado pelo contato com a Empório da Música! Se precisar de algo mais, estamos à disposição. Até logo!")
                break

            print("\n🤖 Assistente: ", end="", flush=True)

            # Executa o streaming de mensagens do grafo
            for event in app.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="values"):
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    
                    # Exibe apenas a resposta final do AIMessage que não contém chamadas pendentes a ferramentas
                    if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                        print(f"\n{last_msg.content}")

        except KeyboardInterrupt:
            print("\n\nAtendimento encerrado.")
            sys.exit(0)
        except Exception as e:
            print(f"\n⚠️ Ocorreu um erro ao processar a mensagem: {str(e)}")

if __name__ == "__main__":
    run_cli()