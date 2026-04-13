HKBU Study Companion - Member C (RAG Module)
=============================================

Files:
- rag_retriever.py: Document processing + BM25 retrieval
- prompt_builder.py: User prompt assembly with context  
- data/processed/chunk_index.json: Pre-processed text chunks (189 chunks)
- requirements.txt: Python dependencies

Usage for Member A:
-------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Initialize RAG in your code:
   from rag_retriever import init_rag, retrieve_context
   
   init_rag()  # Loads the pre-processed index

3. Get context for a query:
   context, results, stats = retrieve_context("Your question here", top_k=3)
   
   Returns:
   - context: Formatted string with citations
   - results: Raw results list
   - stats: Method and count info

4. Build user prompt:
   from prompt_builder import build_user_prompt
   
   user_prompt = build_user_prompt(
       user_query=query,
       retrieved_context=context,
       search_mode=True,
       think_mode=False
   )

Example:
--------
from rag_retriever import init_rag, retrieve_context
from prompt_builder import build_user_prompt

# Initialize once
init_rag()

# Get context
query = "What is the late submission policy?"
context, results, stats = retrieve_context(query, top_k=3)

# Build prompt
user_prompt = build_user_prompt(query, context, search_mode=True)

# Context includes citations like:
# [1] Source: Policy_for_Assessment.pdf, Page 10 (Relevance: 7.76)
# Late submission without prior approval will not be accepted...

Dependencies:
- pypdf: PDF parsing
- rank-bm25: Lexical retrieval
- chromadb: Vector database (optional, for neural retrieval)

Note on Neural Retrieval:
-------------------------
Neural retrieval code is implemented in rag_retriever.py (build_vector_index method).
Due to torch dependency issues on local Windows, it was not executed.
To test neural retrieval, run on Google Colab or Linux environment.

Contact:
Member C - RAG Module