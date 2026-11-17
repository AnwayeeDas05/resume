import os
import logging
import numpy as np
from typing import List, Union

# Optimize offline operation: prevent HF hub HTTP lookup timeouts
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from app.config import settings


logger = logging.getLogger("resume_matcher.model_loader")

_model_instance = None

def get_sentence_transformer() -> SentenceTransformer:
    """
    Returns the cached singleton SentenceTransformer model.
    """
    global _model_instance
    if _model_instance is None:
        logger.info(f"Loading SentenceTransformer: {settings.SENTENCE_TRANSFORMER_MODEL}")
        _model_instance = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    return _model_instance

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculates cosine similarity between two 1D embedding vectors.
    Returns float in range [-1.0, 1.0], normalized to [0.0, 1.0].
    """
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    sim = float(np.dot(vec1, vec2) / (norm1 * norm2))
    # Normalize between 0.0 and 1.0
    return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

def encode_texts(texts: List[str]) -> np.ndarray:
    """Encodes a list of strings into dense vectors using all-MiniLM-L6-v2."""
    model = get_sentence_transformer()
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
