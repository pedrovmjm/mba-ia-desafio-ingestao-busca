# Ingestão e Busca Semântica com LangChain e Postgres

## 🎯 Funcionalidades
- **Ingestão**: Processar arquivos PDF e armazenar em banco vetorial PostgreSQL
- **Chat**: Interface CLI para perguntas baseadas exclusivamente no conteúdo do PDF
- **Chat com histórico**: Interface CLI para perguntas baseadas exclusivamente no conteúdo do PDF e com histórico de conversação.

## 📁 Estrutura do Projeto

```
├── docker-compose.yml         # Configuração PostgreSQL + pgVector
├── requirements.txt           # Dependências Python
├── .env.example              # Template de variáveis de ambiente
├── libs/
│   └── envs/
│       └── env_validator.py  # Validador interativo de variáveis
├── src/
│   ├── ingest.py            # Script de ingestão do PDF
│   ├── search.py            # Script de busca semântica
│   ├── chat.py              # Interface CLI interativa
│   └── chat_with_history.py # Interface CLI interativa com histórico de conversação
├── document.pdf             # PDF de exemplo para ingestão
└── README.md               # Este arquivo
```

## 🛠️ Tecnologias
- **Python 3.10+** com tipagem
- **LangChain** para processamento de documentos
- **PostgreSQL + pgVector** para armazenamento vetorial
- **Google Gemini** para embeddings e geração de respostas
- **Docker Compose** para infraestrutura

## Pré-requisitos
- Python 3.10+
- Docker e Docker Compose
- Chave de API do Google Gemini

## Configuração

### 1. Ambiente Virtual
Crie e ative um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependências
Instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e preencha as variáveis:
```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```env
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

**Importante**: Substitua `your_google_api_key_here` pela sua chave de API do Google Gemini.

## Ordem de Execução

### 1. Subir o banco de dados:
```bash
docker compose up -d
```

### 2. Executar ingestão do PDF:
```bash
python src/ingest.py
```

### 3. Rodar o chat:
```bash
python3 src/chat.py
```

### 4. Rodar o chat com histórico:
```bash
python3 src/chat_with_history.py
```

## 💬 Como Usar o CLI

### Interface do Chat
O sistema oferece uma interface de linha de comando interativa:

```
🔍 Validando variáveis de ambiente...
📋 Variáveis configuradas:
  ✅ GOOGLE_API_KEY = AIzaSyAU...
  ✅ DATABASE_URL = postgresql+psycopg://postgres:postgres@localhost:5432/rag
  ✅ PG_VECTOR_COLLECTION_NAME = pdf_chunks
  ✅ PDF_PATH = document.pdf
✅ Todas as variáveis de ambiente estão configuradas!

Faça sua pergunta (digite 'sair' para encerrar):

PERGUNTA DO USUÁRIO: me fala sobre o documento
RESPOSTA DO MODEL: O documento contém uma lista de empresas, seus respectivos setores de atuação, receita (em reais) e ano de fundação. As empresas estão agrupadas por nomes que começam com "Épico", "Ímpar", "Tríade", "Vale", "Grão", "Aliança", "Esmeralda" e "Cobalto".

PERGUNTA DO USUÁRIO: qual empresa tem maior receita?
RESPOSTA DO MODEL: [Resposta baseada no conteúdo do PDF]

PERGUNTA DO USUÁRIO: qual é a capital da França?
RESPOSTA DO MODEL: Não tenho informações necessárias para responder sua pergunta.

PERGUNTA DO USUÁRIO: sair
Encerrando chat.
```

### Comandos Disponíveis
- **Qualquer pergunta**: O sistema busca no conteúdo do PDF e responde
- **`sair`**, **`exit`**, **`quit`**: Encerra o chat

## ⚙️ Requisitos do Projeto

### 📄 Ingestão do PDF
- **Chunking**: PDF dividido em pedaços de 1000 caracteres com sobreposição de 150 ✅
- **Embeddings**: Cada chunk convertido em vetor usando `models/embedding-001` do Gemini ✅
- **Armazenamento**: Vetores salvos no PostgreSQL com extensão pgVector ✅

### 🔍 Busca Semântica
- **Interface CLI**: Chat interativo no terminal ✅
- **Busca vetorial**: Encontra os 10 chunks mais relevantes (k=10) ✅
- **Geração de resposta**: LLM Gemini processa contexto e responde ✅
- **Validação de contexto**: Responde apenas com base no PDF ingerido ✅


## 🔧 Detalhes Técnicos

### Prompt Template Chat
O sistema utiliza o template disponibilizado pelo LangChain para garantir respostas baseadas apenas no contexto:

```python
PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""
```

### Fluxo de Dados
1. **PDF → Chunks**: Documento dividido em pedaços de 1000 caracteres
2. **Chunks → Embeddings**: Vetorização usando Gemini embeddings
3. **Embeddings → PostgreSQL**: Armazenamento com pgVector
4. **Query → Busca**: Similaridade semântica nos vetores
5. **Contexto → LLM**: Geração de resposta com Gemini


## 🎁 Bônus: Chat com Histórico Conversacional

> **Observação**: O chat com histórico conversacional foi implementado, entretanto, o prompt teve que ser alterado para adequar o comportamento do modelo, portanto, não foi utilizado o prompt fornecido anteriormente.

### 💬 Funcionalidade Extra
Além do chat básico, implementei um **chat com memória conversacional**:

```bash
python3 src/chat_with_history.py
```

### ✨ Recursos Adicionais
- **Memória de conversa**: Mantém contexto entre perguntas
- **Sessões independentes**: Múltiplos usuários simultâneos
- **Comandos especiais**:
  - `historico` - Ver histórico da conversa
  - `limpar` - Limpar memória da sessão
  - `sair` - Encerrar chat
- **Interface aprimorada**: Emojis e formatação visual


### 🔄 Exemplo de Uso Conversacional
```
🤖 Chat com Histórico - Sistema de Busca Semântica
==================================================
🔍 Validando variáveis de ambiente...
📋 Variáveis configuradas:
  ✅ GOOGLE_API_KEY = AIzaSyAU...
  ✅ DATABASE_URL = postgresql+psycopg://postgres:postgres@localhost:5432/rag
  ✅ PG_VECTOR_COLLECTION_NAME = pdf_chunks
  ✅ PDF_PATH = document.pdf
✅ Todas as variáveis de ambiente estão configuradas!

Comandos especiais:
- 'sair', 'exit', 'quit': Encerrar chat
- 'limpar', 'clear': Limpar histórico
- 'historico', 'history': Ver histórico

FAÇA SUA PERGUNTA: me fala sobre a primeira empresa no contexto
RESPOSTA DO MODELO: A primeira empresa no contexto é a Épico Imobiliária Serviços, com receita de R$ 12.800.650,98 e fundada em 1970.

FAÇA SUA PERGUNTA: qual é o nome dela ?
RESPOSTA DO MODELO: Épico Imobiliária Serviços.

FAÇA SUA PERGUNTA: e da  Alfa Imobiliária S.A ?
RESPOSTA DO MODELO: A Alfa Imobiliária S.A. teve um faturamento de R$ 666.804.293,08 e foi fundada em 2012.

FAÇA SUA PERGUNTA: historico

Histórico da conversa:
1. VOCÊ: me fala sobre a primeira empresa no contexto
2. ASSISTENTE: A primeira empresa no contexto é a Épico Imobiliária Serviços, com receita de R$ 12.800.650,98 e fun...
3. VOCÊ: qual é o nome dela ?
4. ASSISTENTE: Épico Imobiliária Serviços.
5. VOCÊ: e da  Alfa Imobiliária S.A ?
6. ASSISTENTE: A Alfa Imobiliária S.A. teve um faturamento de R$ 666.804.293,08 e foi fundada em 2012.

```

### 🏗️ Arquitetura Conversacional
- **`ConversationalSearchService`**: Classe principal com memória
- **`InMemoryChatMessageHistory`**: Armazenamento de sessões
- **Message Trimming**: Mantém últimas 10 mensagens
- **Context Integration**: Combina busca semântica + histórico

## 📊 Status do Projeto

✅ **Funcionalidades Implementadas**:
- Ingestão de PDF com chunking
- Armazenamento vetorial PostgreSQL + pgVector
- Busca semântica com k=10
- Interface CLI interativa
- Validação de variáveis de ambiente
- Tipagem Python
- Classe SearchService organizada
- **🎁 Chat com histórico conversacional**

✅ **Evidências de testes**:
- Docker Compose com PostgreSQL
- Ingestão completa (67 chunks processados)
- Chat respondendo perguntas sobre o documento
- Rejeição de perguntas fora do contexto
- **Chat conversacional mantendo contexto**

---
**🎓 Desenvolvido para o desafio MBA Engenharia de Software com IA - Full Cycle**
