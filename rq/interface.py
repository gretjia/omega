# Filename: rq/interface.py
import sys
import os

# Ensure the package is in path if needed (though we are inside it)
# Expose submodules

from .data.adapter import OmegaDataAdapter
from .factor.maxwell_operators import MaxwellOperators
from .alpha.runner import OmegaAlphaRunner
# Optimizer placeholder
# from .optimizer.solver import OmegaSolver

class OmegaRQ:
    _data_adapter = None
    _alpha_runner = None
    
    @classmethod
    def init(cls, config_path="d:/OMEGA/rq/config.yaml"):
        cls._data_adapter = OmegaDataAdapter(config_path)
        cls._alpha_runner = OmegaAlphaRunner(config_path)
        print("OmegaRQ Initialized.")
        
    @property
    def data(self):
        if not self._data_adapter: self.init()
        return self._data_adapter
        
    @property
    def factor(self):
        return MaxwellOperators
        
    @property
    def alpha(self):
        if not self._alpha_runner: self.init()
        return self._alpha_runner

# Singleton instance
api = OmegaRQ()
