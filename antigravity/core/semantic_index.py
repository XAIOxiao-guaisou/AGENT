"""
Semantic Index - The Cortex of Antigravity 🧠
=============================================

Powering the "Intent-based Search" for the Neural Nexus.
Transforming Antigravity from a code store to a "meaning store".

Implementation:
- Lightweight TF-IDF (Term Frequency - Inverse Document Frequency).
- Inverted Index for O(1) term lookup.
- No heavy ML dependencies (Industrial Grade).
"""

import math
import re
import logging
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Any

logger = logging.getLogger("antigravity.cortex")

class SemanticIndex:
    """
    A lightweight, industrial-grade semantic search engine.
    Uses TF-IDF and Inverted Indices to match "Intent" rather than just names.
    """
    
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'if', 'else', 'for', 'while', 'return',
        'def', 'class', 'import', 'from', 'in', 'is', 'not', 'to', 'of', 'with',
        'as', 'self', 'none', 'true', 'false', 'todo', 'fixme'
    }

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {} # doc_id -> metadata
        self.inverted_index: Dict[str, List[str]] = defaultdict(list) # term -> [doc_ids]
        self.doc_vectors: Dict[str, Dict[str, float]] = {} # doc_id -> {term: score}
        self.doc_freqs: Counter = Counter() # term -> count of docs containing it
        self.total_docs: int = 0
        self._dirty: bool = False

    def learn(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """
        Ingest wisdom (code/docs) into the cortex.
        """
        if not text:
            return

        # Tokenize
        tokens = self._tokenize(text)
        if not tokens:
            return

        # Store Metadata
        self.documents[doc_id] = metadata or {}
        
        # Update Statistics
        term_counts = Counter(tokens)
        self.doc_vectors[doc_id] = {t: c for t, c in term_counts.items()} # Store raw TF first
        
        for term in term_counts:
            self.inverted_index[term].append(doc_id)
            self.doc_freqs[term] += 1
            
        self.total_docs += 1
        self._dirty = True
        logger.debug(f"🧠 Cortex learned: {doc_id} ({len(tokens)} tokens)")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for intent.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Candidate selection (Union of all documents containing any query term)
        candidates = set()
        for term in query_tokens:
            candidates.update(self.inverted_index.get(term, []))

        if not candidates:
            return []

        # Scoring (TF-IDF Cosine Similarity adjacent)
        # Simplified: Sum of (TF_doc * IDF * TF_query)
        scores: Dict[str, float] = defaultdict(float)
        
        for term in query_tokens:
            idf = self._calculate_idf(term)
            query_weight = 1.0 * idf # Assume query TF is 1 for short queries
            
            # Lookup pre-calculated docs
            # Optimization: use pre-calculated inverted list structure only?
            # We iterate candidates to support loose coupling
            for doc_id in self.inverted_index.get(term, []):
                # Raw TF in doc
                raw_tf = self.doc_vectors[doc_id].get(term, 0.0)
                # Log normalization for TF
                tf = 1 + math.log(raw_tf) if raw_tf > 0 else 0
                
                # Boost if term in name (if available in metadata)
                boost = 1.0
                if self.documents[doc_id].get('name') and term in self.documents[doc_id]['name'].lower():
                    boost = 2.0
                
                scores[doc_id] += tf * idf * query_weight * boost

        # Sort and Format
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in ranked:
            meta = self.documents[doc_id].copy()
            meta['score'] = round(score, 4)
            meta['id'] = doc_id
            results.append(meta)
            
        return results

    def _tokenize(self, text: str) -> List[str]:
        """
        Industrial Tokenizer: Splits on camelCase, snake_case, and whitespace.
        """
        # 1. Replace symbols with space
        clean_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        
        # 2. Split camelCase (e.g., FleetModuleLoader -> Fleet Module Loader)
        # This regex looks for: (lower)(Upper) -> \1 \2
        clean_text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', clean_text)
        
        # 3. Lowercase and split
        tokens = clean_text.lower().split()
        
        # 4. Filter Stopwords & Short tokens
        valid_tokens = []
        for t in tokens:
            if t in self.STOP_WORDS or len(t) < 3:
                continue
            # Micro-Stemming for recall
            stemmed = self._stem(t)
            valid_tokens.append(stemmed)
        
        return valid_tokens

    def _stem(self, word: str) -> str:
        """
        Micro-Stemmer (Industrial/Lightweight).
        """
        if len(word) < 4: return word
        if word.endswith('ing'): return word[:-3]
        if word.endswith('ly'): return word[:-2]
        if word.endswith('ed'): return word[:-2]
        if word.endswith('s') and not word.endswith('ss'): return word[:-1]
        if word.endswith('er'): return word[:-2]
        return word

    def _calculate_idf(self, term: str) -> float:
        """
        Calculate Inverse Document Frequency.
        IDF = log(TotalDocs / (DocFreq + 1)) + 1
        """
        df = self.doc_freqs.get(term, 0)
        return math.log((self.total_docs + 1) / (df + 1)) + 1.0
