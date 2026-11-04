
# Criação de um agente de comunicação para a empresa Empório Músicas

## Objetivos

Assumir uma **persona** alinhada com a identidade e o tom da loja.
*  Receber e responder mensagens com base no contexto disponibilizado.
*  Saber quando consultar dados (ex.: disponibilidade, preços, status de pedido) e
quando consultar políticas (ex.: regras de troca, horários, formas de pagamento).
*  Lidar adequadamente com perguntas que fujam do escopo da loja.

## Decisões Técnicas

* Frameworks -> RAG, LangChain/LangGraph

* Modelo Provedor -> OpenRouter with Openai as fallback

* Interface de Iteração -> Gradio/Streamlit

* Persistência do histórico de conversa -> Implemente se fizer sentido para a experiência do usuário.
Tratamento dos dados -> Se for necessário


# RoadMap

1.  **Configuração do Ambiente, Estrutura de Pastas e Carga dos Dados**
            (Pydantic Settings, Ingestão CSV -> SQLite, Indexação PDF -> FAISS RAG)

2.  **Implementação das Ferramentas (Tools)**
            (Tool SQL para Consultas e Tool RAG para Políticas com tipagem Pydantic)

3.  **Modelo com Fallback (OpenRouter -> OpenAI) e Observabilidade (LangSmith)**
            (Configuração da LLM resiliente e rastreamento de execução)

4. **Construção do Agente e Persona com LangGraph**
            (System Prompt estrito, máquina de estados e roteamento de tools)

5. **Validação, Testes dos Cenários do Entregável e README Final**
            (Execução dos cenários de teste, geração dos arquivos de log e documentação)











