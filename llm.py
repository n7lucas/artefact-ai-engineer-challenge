import os
from langchain_openai import ChatOpenAI
from config import settings
from typing import List, Any

def init_observability():
    """Garante que as variáveis de ambiente do LangSmith estejam ativas no processo."""
    if settings.langchain_tracing_v2 and settings.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        print("📊 LangSmith Observability: Ativado.")
    else:
        print("ℹ️ LangSmith Observability: Desativado (chave de API não fornecida).")

def get_resilient_llm(tools: List[Any] = None) -> Any:
    """Configura o modelo principal via OpenRouter com fallback automático para a API direta da OpenAI."""
    init_observability()

    
    if settings.openrouter_api_key and settings.openrouter_api_key.strip():
        primary_llm = ChatOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=settings.primary_model,
            temperature=0.2
        )

        fallback_llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.fallback_model,
            temperature=0.2
        )

      
        if tools:
            primary_with_tools = primary_llm.bind_tools(tools)
            fallback_with_tools = fallback_llm.bind_tools(tools)
            return primary_with_tools.with_fallbacks([fallback_with_tools])

        
        
        return primary_llm.with_fallbacks([fallback_llm])

    
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.fallback_model,
        temperature=0.2
    )