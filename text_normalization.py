#!/usr/bin/env python3
"""
Text Normalization
====================================================

Este script aplica normalización de texto a los corpus de ArXiv y PubMed
siguiendo los siguientes pasos:
1. Tokenization
2. Remove stop words (articles, prepositions, conjunctions, pronouns) usando POS tagging
3. Lemmatization

Input files: arxiv_raw_corpus.csv, pubmed_raw_corpus.csv
Output files: arxiv_normalized_corpus.csv, pubmed_normalized_corpus.csv
"""

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer
import re

# Download NLTK data si no está disponible
def download_nltk_data():
    required_data = [
        'punkt', 
        'punkt_tab',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng', 
        'wordnet', 
        'omw-1.4'
    ]
    for data in required_data:
        try:
            nltk.download(data, quiet=True)
            print(f"Downloaded {data}")
        except Exception as e:
            print(f"Warning: Could not download {data}: {e}")

class TextNormalizer:
    """Simple text normalizer para scientific documents"""
    
    def __init__(self):
        download_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        
        # POS tags para grammatical categories que queremos remover
        self.stop_pos_tags = {
            'DT',    # Articles (a, an, the)
            'IN',    # Prepositions (in, of, at, by, for, with, etc.)
            'CC',    # Conjunctions (and, but, or, etc.)
            'PRP',   # Personal pronouns (I, he, she, it, etc.)
            'PRP$'   # Possessive pronouns (my, his, her, its, etc.)
        }
    
    def normalize_text(self, text):
        """
        Apply complete normalization process to text
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Normalized text
        """
        if pd.isna(text) or not text:
            return ""
        
        # Clean text básico
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        
        # Step 1: Tokenization
        tokens = word_tokenize(text)
        
        # Step 2: POS tagging para identificar grammatical categories
        pos_tagged = pos_tag(tokens)
        
        # Step 3: Remove stop words basado en POS tags
        filtered_tokens = []
        for token, pos in pos_tagged:
            # Keep only alphabetic tokens que no son stop word categories
            if (token.isalpha() and 
                pos not in self.stop_pos_tags and 
                len(token) > 1):  # Remove single letters
                filtered_tokens.append(token)
        
        # Step 4: Lemmatization
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in filtered_tokens]
        
        # Return como space-separated string
        return ' '.join(lemmatized_tokens)

def process_corpus():
    """Main function para procesar both corpora"""
    
    print("Starting text normalization...")
    
    # Initialize normalizer
    normalizer = TextNormalizer()
    
    try:
        # Load ArXiv corpus
        print("Loading ArXiv corpus...")
        arxiv_df = pd.read_csv('arxiv_raw_corpus.csv', sep='\t')
        print(f"    Loaded {len(arxiv_df)} ArXiv documents")
        
        # Load PubMed corpus
        print("Loading PubMed corpus...")
        pubmed_df = pd.read_csv('pubmed_raw_corpus.csv', sep='\t')
        print(f"    Loaded {len(pubmed_df)} PubMed documents")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find input files - {e}")
        return
    
    # Process ArXiv corpus
    print("Processing ArXiv documents...")
    arxiv_normalized = arxiv_df.copy()
    
    for idx, row in arxiv_df.iterrows():
        # Normalize Title field
        if pd.notna(row['Title']):
            arxiv_normalized.at[idx, 'Title'] = normalizer.normalize_text(row['Title'])
        
        # Normalize Abstract field
        if pd.notna(row['Abstract']):
            arxiv_normalized.at[idx, 'Abstract'] = normalizer.normalize_text(row['Abstract'])
        
        # Progress update cada 50 docs
        if (idx + 1) % 50 == 0:
            print(f"=======>>> Processed {idx + 1}/{len(arxiv_df)} ArXiv documents")
    
    # Process PubMed corpus
    print("Processing PubMed documents...")
    pubmed_normalized = pubmed_df.copy()
    
    for idx, row in pubmed_df.iterrows():
        # Normalize Title field
        if pd.notna(row['Title']):
            pubmed_normalized.at[idx, 'Title'] = normalizer.normalize_text(row['Title'])
        
        # Normalize Abstract field  
        if pd.notna(row['Abstract']):
            pubmed_normalized.at[idx, 'Abstract'] = normalizer.normalize_text(row['Abstract'])
        
        # Progress update cada 50 docs
        if (idx + 1) % 50 == 0:
            print(f"=======>>> Processed {idx + 1}/{len(pubmed_df)} PubMed documents")
    
    # Save normalized corpora con el mismo format
    print("Saving normalized corpora...")
    arxiv_normalized.to_csv('arxiv_normalized_corpus.csv', sep='\t', index=False)
    pubmed_normalized.to_csv('pubmed_normalized_corpus.csv', sep='\t', index=False)
    
    print(")))))Text normalization completed successfully!")

if __name__ == "__main__":
    process_corpus()
