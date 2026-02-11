import sys
import os
import importlib
from typing import Any, Dict, List

# Add project root to path to find omega_v3_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from pipeline.interfaces.math_core import IMathCore

class OmegaCoreAdapter(IMathCore):
    """
    Adapts the 'omega_core' to the new 'IMathCore' interface.
    """
    
    def __init__(self):
        self._kernel_module = None
        self._config = {}
        
    @property
    def version(self) -> str:
        return "5.0.0-CoreAdapter"

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Dynamically imports omega_core to avoid strict dependencies at module level.
        """
        self._config = config
        try:
            # Dynamic import allows the pipeline to load even if v3 folder is missing (for v4 users)
            self._kernel_module = importlib.import_module("omega_core.kernel")
            print(f"[{self.version}] omega_core.kernel loaded successfully.")
        except ImportError as e:
            raise RuntimeError(f"Failed to load core: {e}")

    def process_frame(self, frame_id: str, data: Any) -> Any:
        """
        Delegates to v3's apply_recursive_physics.
        Assumes 'data' is a Polars DataFrame as per v3 convention.
        """
        if not self._kernel_module:
            raise RuntimeError("Core not initialized. Call initialize() first.")
        
        cfg = self._config.get("pipeline_cfg")
        if not cfg:
             from config import L2PipelineConfig
             cfg = L2PipelineConfig()

        return self._kernel_module.apply_recursive_physics(data, cfg)

    def get_feature_schema(self) -> List[str]:
        # Hardcoded for v3 compatibility, or loaded from v3 config
        return ["dv_k", "ret_k", "residual_k", "epiplexity"]

    def validate_orthogonality(self, pnl_vector: Any, physics_vector: Any) -> float:
        # Placeholder: v3 orthogonality logic
        return 0.01  # Mock value
