# Filename: rq/scanner.py
# ROLE: The Optimization Controller (RQAlpha-based)

import itertools
import pandas as pd
import sys
import os
from concurrent.futures import ProcessPoolExecutor

# Import local interface
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rq.interface import OmegaRQ

PARAM_GRID = {
    'gamma': [30.0, 50.0, 70.0],
    'vol_threshold': [5000.0, 10000.0]
}

def run_simulation(args):
    code, params = args
    # How to pass params to runner?
    # We can modify config.yaml temporarily or pass via some context injection?
    # Runner accepts strategy functions. We can use a closure.
    
    # Define strategy with captured params
    def init(context):
        # Inject params
        context.omega_cfg = {'physics': params}
        context.controllers = {}
        # ... load brain ...
        from kernel import NumpyBrain
        context.brain = NumpyBrain("omega_brain_v24.pkl") # Use v24 brain
        subscribe(code)
        
    def handle_tick(context, tick):
        # Use the standard strategy logic but with our dynamic context
        # We need to import the logic from strategy.py but bind it here
        from rq.alpha.strategy import handle_tick as standard_tick
        standard_tick(context, tick)
        
    # Run
    # OmegaRQ.alpha is an instance of OmegaAlphaRunner
    # We create a new runner instance to avoid state issues in threads?
    # Actually runner is stateless except for config.
    
    res = OmegaRQ.alpha.run_backtest(init, handle_tick, "2025-01-01", "2025-01-10", capital=100000)
    
    if res and 'sys_analyser' in res:
        return res['sys_analyser']['summary']['total_returns']
    return -1.0

def scan():
    print(">>> RQSDK INDUSTRIAL SCANNER <<<")
    OmegaRQ.init()
    
    keys, values = zip(*PARAM_GRID.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    target_code = "000032.XSHE" # Benchmark
    
    print(f"Scanning {len(combinations)} sets on {target_code}...")
    
    results = []
    # Serial for now to avoid pickling issues with closures, or use ProcessPool with care
    # RQAlpha might have issues with multiprocessing if not careful.
    # Let's run serial for safety in this demo.
    
    for params in combinations:
        print(f"Testing {params}...")
        try:
            ret = run_simulation((target_code, params))
            print(f"-> Return: {ret:.2%}")
            results.append({'params': params, 'return': ret})
        except Exception as e:
            print(f"Error: {e}")
            
    # Rank
    df = pd.DataFrame(results).sort_values('return', ascending=False)
    print("\n=== TOP RESULTS ===")
    print(df.head())
    df.to_csv("rq/scan_results.csv")

if __name__ == "__main__":
    scan()
