# Filename: rq/alpha/runner.py
import os
import pandas as pd
try:
    from rqalpha import run_func
except ImportError:
    run_func = None

class OmegaAlphaRunner:
    def __init__(self, config_path="d:/OMEGA/rq/config.yaml"):
        import yaml
        with open(config_path, 'r') as f:
            self.cfg = yaml.safe_load(f)
        self.bundle_path = self.cfg.get('bundle_path')

    def run_backtest(self, strategy_init=None, strategy_handle_tick=None, start_date=None, end_date=None, capital=1000000, codes=None):
        """
        Run RQAlpha Backtest
        If init/handle_tick are None, load default Maxwell Strategy.
        """
        if run_func is None:
            print("RQAlpha not installed.")
            return None
            
        # Default to standard strategy if not provided
        if strategy_init is None or strategy_handle_tick is None:
            from .strategy import init, handle_tick
            strategy_init = init
            strategy_handle_tick = handle_tick
            
        config = {
            "base": {
                "start_date": start_date,
                "end_date": end_date,
                "benchmark": "000300.XSHG",
                "accounts": {
                    "stock": capital
                },
                "frequency": "tick",
                "data_bundle_path": self.bundle_path
            },
            "extra": {
                "log_level": "info",
            },
            "mod": {
                "sys_analyser": {
                    "enabled": True,
                    "plot": False
                }
            }
        }
        
        # We need to wrap the functions to pass them to run_func
        # But run_func expects a scope.
        # Easier way: Define a module-level generic strategy and inject logic?
        # Or just return the config and let the user call run_func.
        # But we want to encapsulate.
        
        # Let's create a dynamic scope
        scope = {
            "init": strategy_init,
            "handle_tick": strategy_handle_tick,
        }
        
        return run_func(config=config, user_scope=scope)

