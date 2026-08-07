"""Composición del score y recomendaciones."""
from app.scoring.recommendations import build_recommendations
from app.scoring.score import WEIGHTS, compute_score

__all__ = ["WEIGHTS", "build_recommendations", "compute_score"]
