from pathlib import Path
from typing import Dict, Optional
import numpy as np
import torch
import torch.nn as nn


class NeuralRankerModel(nn.Module):
    """
    PyTorch Neural Re-Ranker Architecture (Fix Part 1 §1.2):
    Input: [semantic, keyword, authority, freshness] (4 normalized features)
    Hidden 1: Dense(4 -> 16, ReLU)
    Hidden 2: Dense(16 -> 8, ReLU)
    Output:   Dense(8 -> 1, Sigmoid) -> predicted relevance score (0-1)
    """

    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class NeuralRanker:
    """Wrapper class for PyTorch Neural Re-Ranker inference and SHAP-style feature attribution."""

    def __init__(self, model_path: Optional[Path] = None):
        if model_path is None:
            model_path = Path(__file__).parent / "neural_ranker.pt"
        self.model_path = model_path
        self.model = NeuralRankerModel()
        self.is_trained = False
        self.load_weights()

    def load_weights(self):
        """Load pre-trained PyTorch weights if checkpoint exists."""
        if self.model_path.exists():
            try:
                self.model.load_state_dict(torch.load(self.model_path, map_location="cpu"))
                self.model.eval()
                self.is_trained = True
            except Exception as e:
                print(f"Could not load neural ranker weights: {e}")
                self.is_trained = False
        else:
            self.is_trained = False

    def predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        """
        Input: (N, 4) numpy array of normalized [semantic, keyword, authority, freshness] scores.
        Output: (N,) numpy array of predicted neural relevance scores in [0.0, 1.0].
        """
        if feature_matrix.size == 0:
            return np.array([])

        self.model.eval()
        with torch.no_grad():
            tensor_in = torch.tensor(feature_matrix, dtype=torch.float32)
            scores = self.model(tensor_in).squeeze(-1).numpy()
            if scores.ndim == 0:
                scores = np.array([float(scores)])
            return np.clip(scores, 0.0, 1.0)

    def compute_feature_attributions(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """
        Compute gradient-based feature importance attributions for explainability (§1.2).
        Returns dict of feature contributions for [semantic, keyword, authority, freshness].
        """
        feature_names = ["semantic", "keyword", "authority", "freshness"]
        if not self.is_trained:
            return {f: round(float(feature_vector[idx] * 0.25), 4) for idx, f in enumerate(feature_names)}

        self.model.eval()
        x = torch.tensor(feature_vector, dtype=torch.float32, requires_grad=True)
        out = self.model(x)
        out.backward()

        if x.grad is not None:
            grads = x.grad.abs().numpy()
        else:
            grads = np.ones(4)

        total_grad = np.sum(grads) + 1e-8
        norm_grads = grads / total_grad

        attributions = {}
        for idx, f in enumerate(feature_names):
            val = float(feature_vector[idx] * norm_grads[idx])
            attributions[f] = round(val, 4)

        return attributions
