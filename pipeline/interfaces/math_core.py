from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd
# If Polars is used, we type hint for it, but keep it loose for compatibility
# from polars import DataFrame as PlDataFrame

class IMathCore(ABC):
    """
    The Abstract Interface for OMEGA Physics Kernels.
    Any math core version (v3, v4, v5) must implement this adapter.
    """

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the version string (e.g., '3.1.0')."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Load weights, constants, and recursive state definitions.
        """
        pass

    @abstractmethod
    def process_frame(self, frame_id: str, data: Any) -> Any:
        """
        Apply the recursive physics transform to a single dataframe (Tick -> Snapshot).
        Input/Output types are generic (Any) to support switching between Pandas/Polars/Arrow.
        """
        pass

    @abstractmethod
    def get_feature_schema(self) -> List[str]:
        """
        Return the list of columns that this core produces for training.
        Used by the Trainer to validate input data.
        """
        pass

    @abstractmethod
    def validate_orthogonality(self, pnl_vector: Any, physics_vector: Any) -> float:
        """
        Calculate the Orthogonality metric (Ephemeral Quality).
        """
        pass
