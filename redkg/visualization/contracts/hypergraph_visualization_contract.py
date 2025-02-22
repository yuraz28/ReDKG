"""HypergraphVisualizationContract module."""

from dataclasses import dataclass
from typing import Optional

from redkg.visualization.config.parameters.edge_styles import EdgeStyles
from redkg.visualization.contracts.base_visualization_contract import BaseVisualizationContract
from redkg.visualization.contracts.hypergraph_contract import HypergraphContract


@dataclass
class HypergraphVisualizationContract(BaseVisualizationContract):
    """Hypergraph  visualization contract base class."""

    graph: Optional[HypergraphContract] = None
    edge_style: str = EdgeStyles.circle
