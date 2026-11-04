import json
import sqlite3
from typing import List, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from config import settings
from database import init_database
from rag import build_policy_vectorstore

# ------------------------------------------------------------------
# Input Schemas (Pydantic v2)
# ------------------------------------------------------------------

class SQLQueryInput(BaseModel):
    query: str = Field(
        description=(
            "Query SQL SELECT válida para consultar o banco de dados da loja. "
            "Tabelas disponíveis: products, categories, customers, orders, order_items, promotions. "
            "Visão disponível: v_active_promotions."
        )
    )

class PolicySearchInput(BaseModel):
    query: str = Field(
        description=(
            "Pergunta ou termos de busca sobre as políticas e procedimentos da loja "
            "(ex: 'regras de devolução', 'prazo de entrega', 'garantia', 'formas de parcelamento')."
        )
    )

# ------------------------------------------------------------------
# (Factory Pattern)
# ------------------------------------------------------------------

def create_emporio_tools(db_conn: sqlite3.Connection = None, retriever: Any = None) -> List[Any]:
    """Cria e encapsula as ferramentas do agente garantindo acesso ao banco e ao RAG."""
    
   
    conn = db_conn or init_database()
    policy_retriever = retriever or build_policy_vectorstore()

    @tool("query_store_database", args_schema=SQLQueryInput)
    def query_store_database(query: str) -> str:
        """Executa consultas de leitura (SELECT) no banco de dados operacional da Empório da Música.
        Utilize esta ferramenta para verificar estoque, consultar preços, filtrar produtos por especificações técnicas, 
        verificar status de pedidos de clientes e consultar promoções ativas.
        """
        try:
            clean_query = query.strip()
            if not clean_query.lower().startswith("select"):
                return json.dumps({"error": "Segurança: Apenas consultas de leitura (SELECT) são permitidas."})

            cursor = conn.cursor()
            cursor.execute(clean_query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            

            results = [dict(zip(columns, row)) for row in rows]
            
    
            return json.dumps(results[:15], ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Erro de sintaxe na consulta SQL: {str(e)}"})

    @tool("search_store_policies", args_schema=PolicySearchInput)
    def search_store_policies(query: str) -> str:
        """Consulta o manual interno oficial de políticas e procedimentos da Empório da Música.
        Utilize esta ferramenta para responder dúvidas sobre direito de arrependimento, prazos de troca, 
        garantia do fabricante, regras de frete grátis, parcelamento sem juros e horário de funcionamento.
        """
        try:
            docs = policy_retriever.invoke(query)
            if not docs:
                return "Nenhuma política correspondente encontrada no manual."
                
            formatted_results = []
            for doc in docs:
                page_num = doc.metadata.get("page", "N/A")
                formatted_results.append(f"[Página {page_num}]: {doc.page_content}")

            return "\n---\n".join(formatted_results)

        except Exception as e:
            return f"Erro ao consultar políticas: {str(e)}"

    return [query_store_database, search_store_policies]