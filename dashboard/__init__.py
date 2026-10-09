"""Visualizzazioni figure paper: top ROI, top edges (PNG headless).

Posizione nella pipeline: visualizzazione dei risultati degli STEP 1-7 (nessuna elaborazione di pipeline).
"""

from dashboard.plot_top_features import plot_top_edges, plot_top_roi

__all__ = [
    "plot_top_roi",
    "plot_top_edges",
]
