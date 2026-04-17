"""
rag_retriever.py
Member C: Document Processing + RAG Retrieval (Lexical Retrieval Only)
Supports source tracking (filename + page number)
"""

import os
import json
import re
from typing import List, Dict, Tuple, Optional

# PDF processing
from pypdf import PdfReader

# Lexical retrieval
from rank_bm25 import BM25Okapi

# embedding retrieval
from sentence_transformers import SentenceTransformer
import numpy as np


class HKBURetriever:
    """HKBU Study Companion Retriever"""
    
    def __init__(self, data_folder: str, processed_folder: str):
        """
        Initialize retriever
        
        Args:
            data_folder: Folder containing raw PDF files
            processed_folder: Folder to save processed index files
        """
        self.data_folder = data_folder
        self.processed_folder = processed_folder
        self.chunks = []  # Store all text chunks [{text, source, page}]
        self.bm25 = None  # BM25 retriever
        self.embedding_model = None  # embedding retriever
        self.chunk_embeddings = None

        
        # Create processed folder if not exists
        os.makedirs(processed_folder, exist_ok=True)
        
    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Parse a single PDF file, extract text from each page with page numbers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List[Dict]: [{"page": 1, "text": "..."}, ...]
        """
        pages = []
        try:
            reader = PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    # Clean text: remove extra newlines and spaces
                    text = re.sub(r'\n+', '\n', text)
                    text = re.sub(r' +', ' ', text)
                    pages.append({
                        "page": page_num,
                        "text": text.strip()
                    })
            print(f"  Successfully parsed: {os.path.basename(pdf_path)} ({len(pages)} pages)")
        except Exception as e:
            print(f"  Failed to parse: {os.path.basename(pdf_path)} - {e}")
        return pages
    
    def chunk_text(self, pages: List[Dict], source_file: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
        """
        Split text into chunks while preserving source information
        Pure Python implementation, no external dependencies
        
        Args:
            pages: List of parsed pages from parse_pdf
            source_file: Source filename
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap characters between chunks
            
        Returns:
            List[Dict]: [{"text": "...", "source": "...", "page": 1}, ...]
        """
        chunks = []
        
        for page in pages:
            page_text = page["text"]
            page_num = page["page"]
            
            # Simple chunking by character count
            start = 0
            text_length = len(page_text)
            
            while start < text_length:
                end = start + chunk_size
                
                # Try to break at a sentence boundary
                if end < text_length:
                    # Look for good break points within the last 100 chars
                    search_start = max(start + chunk_size - 100, start)
                    for break_char in ['。', '！', '？', '\n', ';', '.', '!', '?', ' ', '\t']:
                        break_pos = page_text.rfind(break_char, search_start, end)
                        if break_pos != -1:
                            end = break_pos + 1
                            break
                
                chunk = page_text[start:end].strip()
                if chunk:
                    chunks.append({
                        "text": chunk,
                        "source": source_file,
                        "page": page_num
                    })
                
                start = end - chunk_overlap if end < text_length else end
        
        print(f"    Generated {len(chunks)} chunks (chunk_size={chunk_size})")
        return chunks
    
    def process_all_documents(self, chunk_size: int = 500, force_reprocess: bool = False):
        """
        Process all documents, generate chunks and indices
        
        Args:
            chunk_size: Maximum characters per chunk
            force_reprocess: Whether to force reprocess (ignore cache)
        """
        print("\nProcessing documents...")
        
        # Check for cache
        index_path = os.path.join(self.processed_folder, "chunk_index.json")
        if os.path.exists(index_path) and not force_reprocess:
            print("  Found existing index file, loading...")
            self.load_index()
            return
        
        # Get all PDF files
        if not os.path.exists(self.data_folder):
            print(f"  Data folder not found: {self.data_folder}")
            print(f"  Please create the folder and put PDF files in it")
            return
            
        pdf_files = [f for f in os.listdir(self.data_folder) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"  No PDF files found in {self.data_folder}")
            print(f"  Please ensure PDF files are placed in: {os.path.abspath(self.data_folder)}")
            return
        
        print(f"  Found {len(pdf_files)} PDF files:")
        for f in pdf_files:
            print(f"    - {f}")
        
        all_chunks = []
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.data_folder, pdf_file)
            print(f"\n  Processing: {pdf_file}")
            
            # Parse PDF
            pages = self.parse_pdf(pdf_path)
            
            # Chunk text
            chunks = self.chunk_text(pages, pdf_file, chunk_size)
            all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        print(f"\nProcessing complete! Generated {len(self.chunks)} chunks total")
        
        # Save index
        self.save_index()
        
        # Build BM25 index
        self.build_bm25_index()

        # Build Embedding Model
        self.build_embedding_model()
        
    def save_index(self):
        """Save chunk index to JSON file"""
        index_path = os.path.join(self.processed_folder, "chunk_index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        print(f"  Index saved to: {index_path}")
    
    def load_index(self):
        """Load chunk index from JSON file"""
        index_path = os.path.join(self.processed_folder, "chunk_index.json")
        with open(index_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        print(f"  Loaded {len(self.chunks)} chunks")
        
        # Build BM25 index
        self.build_bm25_index()

        # Build Embedding Model
        self.build_embedding_model()
    
    def build_bm25_index(self):
        """Build BM25 (lexical retrieval) index"""
        if not self.chunks:
            print("  No chunks available, cannot build BM25 index")
            return
        
        # Tokenize all chunks
        tokenized_chunks = [chunk["text"].split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_chunks)
        print(f"  BM25 index built ({len(self.chunks)} chunks)")
    
    def build_embedding_model(self):
        print("Loading embedding model (first time will download ~100MB)...")
        self.embedding_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        print("✅ Model loaded successfully")

        # Generate embeddings for all chunks
        print(f"Generating embeddings for {len(self.chunks)} chunks (may take 1-2 minutes)...")
        chunk_texts = [chunk["text"] for chunk in self.chunks]
        self.chunk_embeddings = self.embedding_model.encode(chunk_texts, show_progress_bar=True)
        print(f"✅ Embeddings generated, shape: {self.chunk_embeddings.shape}")
    
    def lexical_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Lexical search using BM25
        
        Args:
            query: User question
            top_k: Number of most relevant chunks to return
            
        Returns:
            List[Dict]: [{"text": "...", "source": "...", "page": 1, "score": 12.5}, ...]
        """
        if self.bm25 is None:
            print("BM25 index not built. Please run process_all_documents() first")
            return []
        
        # Tokenize query
        tokenized_query = query.split()
        
        # Get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top_k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                result = self.chunks[idx].copy()
                result["score"] = round(scores[idx], 2)
                results.append(result)
        
        return results

    def neural_search(self, query, top_k=3):
        """Neural search using vector similarity"""
        if self.embedding_model is None:
            print("Embedding model not initialized. Please call build_embeddings() first")
            return []
        if self.chunk_embeddings is None:
            print("Chunk embeddings not generated. Please call build_embeddings() first")
            return []
        query_embedding = self.embedding_model.encode([query])
        similarities = np.dot(self.chunk_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            result = self.chunks[idx].copy()
            result["score"] = float(similarities[idx])
            results.append(result)
        return results
    
    def retrieve(self, query: str, top_k: int = 3, use_embedding_retrieval: bool = False) -> Tuple[List[Dict], Dict]:
        """
        Unified retrieval interface (lexical only for now)
        
        Args:
            query: User question
            top_k: Number of chunks to return
            
        Returns:
            (List of results, Statistics dict)
        """
        # Extract course code from query (e.g., COMP7125, COMP7025)
        course_pattern = r'\b([A-Z]{2,4}[-\s]?[0-9]{4})\b'
        course_match = re.search(course_pattern, query.upper())
        target_course = course_match.group(1).replace(" ", "") if course_match else None
        
        # Retrieve more candidates for filtering (2x top_k)
        expanded_k = top_k * 2 if target_course else top_k
        
        if use_embedding_retrieval:
            results = self.neural_search(query, top_k=expanded_k)
        else:
            results = self.lexical_search(query, top_k=expanded_k)
        
        # Filter and reorder by course code if specified
        if target_course and results:
            matched = [r for r in results if target_course.lower() in r["source"].lower()]
            unmatched = [r for r in results if target_course.lower() not in r["source"].lower()]
            results = (matched + unmatched)[:expanded_k]
        
        stats = {
            "method": "Lexical Retrieval (BM25)" if not use_embedding_retrieval else "Neural Retrieval (Embedding)",
            "num_results": len(results),
            "query": query,
            "target_course": target_course,
            "matched_count": len(matched) if target_course and results else 0
        }
        
        return results, stats
    
    def format_context_with_citations(self, results: List[Dict]) -> str:
        """
        Format retrieval results as context string with citations
        
        Args:
            results: List of results from retrieve()
            
        Returns:
            Formatted context string with citations
        """
        if not results:
            return "(No relevant documents found)"
        
        context_parts = []
        for i, r in enumerate(results, 1):
            citation = f"[{i}] Source: {r['source']}"
            if r.get('page'):
                citation += f", Page {r['page']}"
            citation += f" (Relevance: {r.get('score', 'N/A')})"
            
            context_parts.append(f"{citation}\n{r['text']}\n")
        
        return "\n---\n".join(context_parts)
    
    def get_token_estimate(self, text: str) -> int:
        """
        Estimate token count of text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text) // 2

    def compare_token_usage(self, query: str) -> dict:
            """
            Compare token usage between no-RAG and RAG approaches
            For experiment section in report
            """
            # 1. no RAG's prompt（only questions）
            prompt_no_rag = f"Question: {query}"
            tokens_no_rag = len(prompt_no_rag) // 2
            
            # 2. has RAG's prompt（questions + retrives）
            results, _ = self.retrieve(query, top_k=3)
            context = self.format_context_with_citations(results)
            prompt_with_rag = f"Context:\n{context}\n\nQuestion: {query}"
            tokens_with_rag = len(prompt_with_rag) // 2
            
            return {
                "query": query,
                "no_rag_tokens": tokens_no_rag,
                "with_rag_tokens": tokens_with_rag,
                "extra_tokens_used": tokens_with_rag - tokens_no_rag,
                "num_chunks_retrieved": len(results)
            }

    def run_experiments(self, queries: list) -> list:
            """
            Run token comparison experiments on multiple queries
            """
            results = []
            print("\n" + "=" * 50)
            print("TOKEN EFFICIENCY EXPERIMENTS")
            print("=" * 50)
            
            for query in queries:
                result = self.compare_token_usage(query)
                results.append(result)
                print(f"\nQuery: {query}")
                print(f"  No-RAG tokens: {result['no_rag_tokens']}")
                print(f"  With-RAG tokens: {result['with_rag_tokens']}")
                print(f"  Extra tokens: +{result['extra_tokens_used']}")
                print(f"  Chunks retrieved: {result['num_chunks_retrieved']}")
            
            # print
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            total_no_rag = sum(r['no_rag_tokens'] for r in results)
            total_with_rag = sum(r['with_rag_tokens'] for r in results)
            print(f"Total tokens without RAG: {total_no_rag}")
            print(f"Total tokens with RAG: {total_with_rag}")
            print(f"Average extra tokens per query: {(total_with_rag - total_no_rag) // len(results)}")
            
            return results

# ========== Convenience functions for other members ==========

_global_retriever = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FOLDER = os.path.join(BASE_DIR, "data", "raw")
DEFAULT_PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed")

def get_retriever(data_folder: str = DEFAULT_DATA_FOLDER, processed_folder: str = DEFAULT_PROCESSED_FOLDER) -> HKBURetriever:
    """Get global retriever singleton"""
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = HKBURetriever(data_folder, processed_folder)
    return _global_retriever


def init_rag(force_reprocess: bool = False):
    """
    Initialize RAG system (Called by Member A)
    
    Args:
        force_reprocess: Whether to force reprocess documents
    """
    retriever = get_retriever()
    
    # Process documents
    retriever.process_all_documents(force_reprocess=force_reprocess)
    
    print("\n RAG system initialized successfully!")
    return retriever


def retrieve_context(query: str, top_k: int = 3, use_embedding_retrieval: bool = False) -> Tuple[str, List[Dict], Dict]:
    """
    Retrieve and return formatted context (Called by Member B/D)
    
    Args:
        query: User question
        top_k: Number of chunks to return
        
    Returns:
        (Formatted context string, Raw results list, Statistics dict)
    """
    retriever = get_retriever()
    results, stats = retriever.retrieve(query, top_k, use_embedding_retrieval)
    formatted_context = retriever.format_context_with_citations(results)
    return formatted_context, results, stats


# ========== Test Code ==========
if __name__ == "__main__":
    print("=" * 50)
    print("RAG Retriever Test")
    print("=" * 50)
    
    # Initialize
    retriever = init_rag(force_reprocess=False)
    
    # Test queries
    test_queries = [
        "What are the exam requirements?",
        "What are the group project requirements?",
        "What happens if I submit late?",
    ]
    
    print("\n" + "=" * 50)
    print("Testing Retrieval")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n Query: {query}")
        print("-" * 40)
        
        # Lexical retrieval
        print("\n Lexical Retrieval Results:")
        results_lex, stats_lex = retriever.retrieve(query, top_k=2)
        print(retriever.format_context_with_citations(results_lex))
        print(f"   Estimated Tokens: {retriever.get_token_estimate(query + str(results_lex))}")