
# Agente de comunicação para a empresa Empório da Música

## Instruções de Configuração e Execução
### 1. Pré-requisitos
Python: Versão 3.10 ou superior instalada.

Chaves de API:

OPENROUTER_API_KEY: Provedor principal para modelos abertos/proprietários (opcional se usar apenas OpenAI).

OPENAI_API_KEY: Provedor de backup/fallback obrigatório para Embeddings e resiliência.

LANGCHAIN_API_KEY: Para observabilidade via LangSmith (opcional).


### 2. Configuração do Ambiente Virtual e Dependências
Opção A: Utilizando uv (Recomendado pela velocidade)
```Bash
# 1. Criar e ativar o ambiente virtual
uv venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 2. Instalar dependências
uv pip install -r requirements.txt
```

Opção B: Utilizando pip padrão
```Bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 2. Atualizar o pip e instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuração do Arquivo .env
Crie um arquivo .env na raiz do projeto copiando a estrutura abaixo e preenchendo as suas chaves:
```
# ------------------------------------------------------------------
# Provedores de LLM & Resiliência
# ------------------------------------------------------------------
# Provedor Principal (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-sua-chave-openrouter-aqui
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
PRIMARY_MODEL=openai/gpt-4o-mini

# Provedor de Backup / Fallback (OpenAI Direta)
OPENAI_API_KEY=sk-proj-sua-chave-openai-aqui
FALLBACK_MODEL=gpt-4o-mini

# ------------------------------------------------------------------
# Caminhos do Banco de Dados e PDF
# ------------------------------------------------------------------
DB_PATH=emporio_musica.db
PDF_PATH=políticas_da_loja.pdf

# ------------------------------------------------------------------
# Observabilidade (LangSmith)
# ------------------------------------------------------------------
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_sua-chave-langsmith-aqui
LANGCHAIN_PROJECT=emporio-musica-agent
```


### 4. Validação dos Módulos (Testes Fases 1 a 4)
Antes de iniciar a CLI principal, você pode rodar os scripts de validação para verificar a integridade do banco de dados, RAG, ferramentas e grafo:


```
# Teste de Ingestão de Dados CSV -> SQLite + Indexação RAG
python test_phase1.py

# Teste de Execução Isolada das Ferramentas (SQL + Policy Search)
python test_phase2.py

# Teste da LLM Resiliente (OpenRouter -> OpenAI) e LangSmith
python test_phase3.py

# Teste Completo do Grafo ReAct (LangGraph + Persona Guardrails)
python test_phase4.py
```

### 5. Execução da Interface CLI Interativa
Para rodar o agente em tempo real e conversar no terminal:

```Bash
python main.py
```

Digite a mensagem do cliente e pressione Enter.

Para encerrar a sessão de atendimento no terminal, digite sair, exit ou pressione Ctrl + C.

## Decisões Técnicas


## Framework(s) / abordagem do agente 
**Orquestração** | **LangGraph (ReAct StateGraph)** | Optei por utilizar Langgraph pela facilidade e clareza na criação da estrutura do fluxo do projeto, com isto eu ganho um alto grau de determinismo no fluxo de chamadas de ferramentas e suporte nativo a checkpointers de sessão. A solução optada para trabalhar com os dados em texto e relacionais foi a **hibrida**. Foi utilizado SQL para dados relacionais (produtos e pedidos) e RAG Vetorial (faiss + huggingface) para o PDF de políticas.

**Dados Operacionais** | **SQLite Relacional (In-Memory / Local)** | Ingestão limpa dos arquivos CSV para SQLite. Permite que o LLM execute consultas SQL `SELECT` determinísticas para filtros de catálogo, faixas de preço e verificação exata de estoque. |

## Modelo e Provedor
**LLM & Resiliência** | **OpenRouter (`stealth/crouton-alpha`) + Fallback OpenAI(`gpt-4o-mini`)** | Optei por utilizar um modelo gratuito através do OpenRouter com um fallback para um modelo pago (OpenAI). A configuração foi feita via `.with_fallbacks()` do LangChain. Garante alta disponibilidade caso a API principal sofra indisponibilidade ou *rate limit*.


## Tratamento dos dados
Foram feitas 2 mudanças na base de dados. A primeira mudança foi a remoção de caracteres dos numeros de telefone como "()". A segunda mudança mais substancial foi a Desnormalização do JSON de Especificações (products.specs). A coluna specs contém objetos JSON em texto simples (ex: {"strings":"nylon", "electronics":"no"}). Se mantidos apenas como texto bruto, filtros como "violões de nylon" ou "instrumentos elétricos" exigem seleções complexas com regex. Extrair os campos spec_strings e spec_electronics para colunas dedicadas resolve o problema no SQL. Além disso foi criado uma VIEW *v_active_promotions*, que garante que o cálculo do desconto percentual ocorra via SQL sem risco de erro aritmético do LLM.

## Interface de interação 
Optei por utilizar uma interface simples de CLI mesmo, acredito que para a prototipação o mais importante é toda lógica e input/output estarem funcionando, com a base funcionando como se espera todo o resto fica mais fácil.

## Persistência do histórico de conversa
Foi utilizado MemorySaver e thread_id para persistência do histórico de conversa. Através do thread_id é possivel especificar para o LangGraph qual conversa especifica carregar, enquanto que com o MemorySaver conseguimos salvar o estado da conversa diretamente no processo.




## Limitações

* **Gestão de Memória e Persistência de Sessão**. A forma que o projeto está atualmente é mantida via MemorySaver (armazenamento em memória), uma alternativa mais robusta é utilizar Postgres ou Redis para habilitar que as sessões sobrevivam a reinicialização de servidores.
O número de tokens e latência é algo que precisa ser levado em consideração como alta prioridade quando for escalar o projeto, isso pode ser feito a  partir da criação de um resumo/compactação nas conversas a partir de um limite definido para economizar tokens e reduzir latência.

* **Infraestrutura de Banco de Dados** nosso agente possui somente a permissão de fazer SELECT nos dados, podemos pensar em fazer algo como uma reeserva temporária de estoque, dando mais poder ao agente com comandos como UPDATE/INSERT, mas de forma limitada/controlada. 

* **Outros** Além das já citadas algumas outras melhorias poderiam ser feitas como no Guardrails para aumentar a segurança, fazer uma pipeline mais avançada com RAG e também fazer uma avaliação automatizada dos agentes através de uma pipeline.


## Uso de assistentes de código
Eu utilizei o chat Gemni como assistente para o projeto. Como na pós graduação que estou fazendo eu ja encontrei projetos similares a este, a utilização do Gemni foi um bom complemento de instruções de como eu poderia utilizar as ferramentas utilizadas no meu curso neste projeto e o que eu poderia trazer de novo em relação ao que eu ja sei.




