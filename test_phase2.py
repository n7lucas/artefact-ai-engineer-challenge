from tools import create_emporio_tools

def main():
    print("=== TESTANDO FASE 2: FERRAMENTAS (TOOLS) ===")
    
    # 1. Instancia as ferramentas
    tools = create_emporio_tools()
    sql_tool = tools[0]
    rag_tool = tools[1]
    
    print(f"✅ Ferramentas carregadas: {[t.name for t in tools]}")

    # 2. Teste da Tool SQL
    print("\n--- Testando 'query_store_database' ---")
    sample_sql = "SELECT name, price_brl, stock_quantity FROM products WHERE category_id = 5 AND price_brl <= 1000 LIMIT 3;"
    sql_result = sql_tool.invoke({"query": sample_sql})
    print(f"Resultado SQL:\n{sql_result}")

    # 3. Teste da Tool RAG
    print("\n--- Testando 'search_store_policies' ---")
    rag_result = rag_tool.invoke({"query": "Qual o valor mínimo para frete grátis em Campo Grande?"})
    print(f"Resultado RAG:\n{rag_result}")

if __name__ == "__main__":
    main()