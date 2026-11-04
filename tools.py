import json
import sqlite3
import re
from typing import List, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from config import settings
from database import init_database
from rag import build_policy_vectorstore

# ------------------------------------------------------------------
# Schemas de Entrada (Pydantic v2) com Mapeamento Estrito de Colunas
# ------------------------------------------------------------------

DATABASE_SCHEMA_DOC = """
Query SQL SELECT válida para consultar o banco SQLite da Empório da Música.

NOMES EXATOS DAS COLUNAS (ATENÇÃO AOS NOMES):
1. Tabela `products`:
   - `product_id` (INTEGER)
   - `name` (TEXT) - Ex: 'Yamaha C40 Nylon Natural'
   - `price_brl` (REAL) - Preço em Reais (NÃO USE 'price')
   - `stock_quantity` (INTEGER) - Quantidade em estoque (NÃO USE 'stock' OU 'quantity')
   - `status` (TEXT) - 'active' para produtos disponíveis (NÃO USE 'is_active')
   - `category_id` (INTEGER) - 1: Guitarras, 2: Baixos, 3: Baterias/Percussão, 5: Violões, 9: Ukuleles
   - `spec_strings` (TEXT) - 'nylon' ou 'aço'
   - `spec_electronics` (TEXT) - 'yes' (elétrico) ou 'no' (acústico)
   - `spec_color` (TEXT) - Cor

2. Tabela `categories`: `category_id`, `name`, `description`
3. Tabela `customers`: `customer_id`, `name`, `phone`, `phone_clean`, `email`, `city`
4. Tabela `orders`: `order_id`, `customer_id`, `order_date`, `status`, `total_brl`, `payment_method`, `tracking_code`, `estimated_delivery`
5. Tabela `order_items`: `order_id`, `product_id`, `quantity`
6. Tabela `promotions`: `promotion_id`, `product_id`, `discount_percent`, `description`, `is_active`
7. View `v_active_promotions`: `product_id`, `product_name`, `original_price`, `discount_percent`, `promotional_price`, `promotion_description`
"""

class SQLQueryInput(BaseModel):
    query: str = Field(description=DATABASE_SCHEMA_DOC)

class PolicySearchInput(BaseModel):
    query: str = Field(
        description="Pergunta ou termos de busca sobre as políticas da loja (devolução, entrega, garantia, parcelamento)."
    )

def sanitize_sql(query: str) -> str:
    """Substitui automaticamente alucinações comuns de nomes de colunas."""
    q = query
    q = re.sub(r'\bprice\b', 'price_brl', q, flags=re.IGNORECASE)
    q = re.sub(r'\bstock\b', 'stock_quantity', q, flags=re.IGNORECASE)
    q = re.sub(r'\bis_active\s*=\s*1\b', "status = 'active'", q, flags=re.IGNORECASE)
    return q

# ------------------------------------------------------------------
# Fábrica de Ferramentas
# ------------------------------------------------------------------

def create_emporio_tools(db_conn: sqlite3.Connection = None, retriever: Any = None) -> List[Any]:
    conn = db_conn or init_database()
    policy_retriever = retriever or build_policy_vectorstore()

    @tool("query_store_database", args_schema=SQLQueryInput)
    def query_store_database(query: str) -> str:
        """Executa consultas de leitura (SELECT) no banco de dados operacional da Empório da Música."""
        try:
            clean_query = query.strip()
            if not clean_query.lower().startswith("select"):
                return json.dumps({"error": "Segurança: Apenas consultas SELECT são permitidas."})

            clean_query = sanitize_sql(clean_query)

            # Conexão thread-safe rápida usando o caminho do banco configurado
            local_conn = sqlite3.connect(settings.db_path, check_same_thread=False)
            cursor = local_conn.cursor()
            cursor.execute(clean_query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            local_conn.close()
            
            if not rows:
                return "Nenhum produto ou registro foi encontrado com os critérios pesquisados."

            results = []
            for row in rows:
                item = dict(zip(columns, row))
                if "specs" in item:
                    del item["specs"]
                results.append(item)

            return json.dumps(results[:15], ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Erro na consulta SQL ({str(e)})."})

    @tool("search_store_policies", args_schema=PolicySearchInput)
    def search_store_policies(query: str) -> str:
        """Consulta o manual interno oficial de políticas e procedimentos da Empório da Música."""
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