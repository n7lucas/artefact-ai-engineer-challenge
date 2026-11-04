from database import init_database
from rag import build_policy_vectorstore
import os
def main():
    print("=== TESTANDO FASE 1: BANCO RELACIONAL & RAG ===")
    # 1.SQLite test
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM products WHERE spec_strings = 'nylon';")
    nylon_count = cursor.fetchone()[0]
    print(f"-> Teste SQL: Encontrados {nylon_count} violões com cordas de nylon.")
    
    cursor.execute("SELECT * FROM v_active_promotions LIMIT 2;")
    promos = cursor.fetchall()
    print(f"-> Teste VIEW Promoções: {promos}")
    
    # 2.RAG test
    retriever = build_policy_vectorstore()
    docs = retriever.invoke("Qual a política de devolução por arrependimento?")
    print(f"-> Teste RAG (Devolução): Recorreu {len(docs)} trechos.")
    print(f"   Trecho recuperado (Página {docs[0].metadata['page']}):\n   {docs[0].page_content[:180]}...")

if __name__ == "__main__":
    main()