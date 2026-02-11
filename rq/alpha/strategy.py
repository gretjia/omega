# Filename: rq/alpha/strategy.py
# ROLE: OMEGA v24.00 Standard Strategy Template
# ADAPTER: Maps RQAlpha events to Maxwell Physics Engine

import os
import numpy as np
from rqalpha.api import *

# Import independent modules from rq package
from ..data.adapter import OmegaDataAdapter
from ..factor.maxwell_operators import MaxwellOperators
from ..interface import OmegaRQ

# --- Logic Injection ---
# Instead of depending on kernel.py, we implement a lightweight Controller 
# that uses the rq.factor primitives.

class MaxwellController:
    """ 
    v24.00 Physics Controller (Independent Implementation)
    Manages Volume Clock & Maxwell Inference per stock.
    """
    def __init__(self, code, config):
        self.code = code
        self.vol_threshold = config.get('physics', {}).get('vol_threshold', 10000.0)
        self.lookback = config.get('physics', {}).get('lookback', 120)
        self.gamma = config.get('physics', {}).get('gamma', 50.0)
        
        # State
        self.acc_vol = 0.0
        self.acc_price_list = []
        self.raw_bars = [] # List of np.array [5]
        self.prev_close = None
        
        # Brain Weights (Should be injected or loaded once globally)
        # For now, we assume global 'context.brain' exists or we load it here?
        # Better: Pass Brain in on_tick
        
        self.last_F = 0.0
        
    def on_tick(self, tick, brain):
        price = tick.last
        vol = tick.total_volume # RQ tick volume is cumulative?
        # Wait, RQAlpha tick.total_volume is cumulative for the day.
        # We need delta. This logic is handled by the Strategy Wrapper.
        # Here we assume 'vol' is DELTA volume.
        
        if vol <= 0: return None
        
        self.acc_vol += vol
        self.acc_price_list.append(price)
        
        if self.acc_vol >= self.vol_threshold:
            # --- Volume Bar Complete ---
            o = self.acc_price_list[0]
            c = self.acc_price_list[-1]
            h = max(self.acc_price_list)
            l = min(self.acc_price_list)
            v_bar = self.acc_vol
            
            # Feature Construction (v24 Standard)
            # 1. LogRet
            prev = self.prev_close if self.prev_close else o
            log_ret = np.log(c / (prev + 1e-9))
            self.prev_close = c
            
            # 2. LogVol
            log_vol = np.log1p(v_bar)
            
            # 3. Volatility (Approx range)
            volat = (h - l) / (o + 1e-9)
            
            # 4. Momentum (Instant)
            mom = log_ret
            
            # 5. Spread (Placeholder)
            spread = 0.0
            
            features = np.array([log_ret, log_vol, volat, mom, spread])
            self.raw_bars.append(features)
            
            if len(self.raw_bars) > self.lookback:
                self.raw_bars.pop(0)
                
            # Reset Accumulators
            self.acc_vol = 0.0
            self.acc_price_list = []
            
            # Inference
            if len(self.raw_bars) == self.lookback:
                # [120, 5]
                tensor = np.array(self.raw_bars)
                
                # Use Brain (Maxwell)
                # S: Structural Entropy (Recon Error)
                # E: Kinetic Energy (Magnitude)
                S, E = brain.get_maxwell_state(tensor)
                
                # Maxwell Equation
                # F = E * (1 - tanh(gamma * S))
                # Or simplified Sigmoid Gate
                gate = 1.0 / (1.0 + np.exp(self.gamma * (S - 0.5)))
                F = E * gate
                
                self.last_F = F
                return {'F': F, 'S': S, 'E': E}
                
        return None

# --- RQAlpha Strategy Callbacks ---

def init(context):
    logger.info(">>> OMEGA v24.00 STRATEGY INIT <<<")
    
    # 1. Load Config
    # We can access OmegaRQ.config if exposed, or load yaml directly
    import yaml
    with open("d:/OMEGA/rq/config.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    context.omega_cfg = cfg
    
    # 2. Load Brain (Global Resource)
    # We reuse the NumpyBrain class logic but ensure it pulls from rq/data
    # For simplicity, we assume NumpyBrain is available or we re-implement loading
    from kernel import NumpyBrain # Temporary: In future, move Brain to rq.ai
    context.brain = NumpyBrain("omega_brain_v24.pkl")
    
    # 3. Init Controllers
    context.controllers = {}
    
    # 4. Subscribe
    # For backtest, we might subscribe to a fixed list or dynamic
    target_list = ["000032.XSHE"] # Example
    subscribe(target_list)
    context.targets = target_list
    
    logger.info(f"Subscribed: {target_list}")

def handle_tick(context, tick):
    code = tick.order_book_id
    
    # 1. Controller Management
    if code not in context.controllers:
        context.controllers[code] = MaxwellController(code, context.omega_cfg)
        # Init Volume Tracker for RQ delta calculation
        context.controllers[code]._last_cum_vol = 0.0
        context.controllers[code]._last_date = None
        
    ctl = context.controllers[code]
    
    # 2. Delta Volume Logic (RQAlpha specific)
    current_date = tick.datetime.date()
    if ctl._last_date != current_date:
        ctl._last_cum_vol = 0.0
        ctl._last_date = current_date
        
    delta_vol = tick.total_volume - ctl._last_cum_vol
    if delta_vol < 0: delta_vol = tick.total_volume # Reset detection
    ctl._last_cum_vol = tick.total_volume
    
    if delta_vol <= 0: return
    
    # 3. Physics Inference
    # We modify the Controller to accept delta_vol
    # We construct a pseudo-tick object or pass values
    # Reuse ctl.on_tick signature: tick(obj), brain
    
    # Mock tick object for Controller? 
    # Or refactor Controller to accept (price, vol).
    # Let's Refactor Controller.on_tick to accept values.
    # See below for implementation.
    
    # Using a helper method on ctl for value-based tick
    signal = ctl_on_tick_values(ctl, tick.last, delta_vol, context.brain)
    
    # 4. Execution
    if signal:
        F = signal['F']
        # logger.info(f"SIGNAL {code}: F={F:.4f} S={signal['S']:.4f}")
        
        # Simple Logic: F > 2.0 -> Buy
        if F > 2.0:
            order_target_percent(code, 0.9)
            logger.info(f"BUY {code} @ {tick.last} (F={F:.2f})")
            
    # Exit Logic (Thermodynamics)
    if ctl.last_F < 0.1:
        # Check position
        pos = context.portfolio.positions[code].quantity
        if pos > 0:
            order_target_percent(code, 0.0)
            logger.info(f"EXIT {code} (Entropy Decay)")

def ctl_on_tick_values(ctl, price, vol, brain):
    """ Helper to bridge RQ data to Controller logic """
    # This effectively replaces ctl.on_tick inside the class
    # To keep class clean, we use this external function or method
    
    ctl.acc_vol += vol
    ctl.acc_price_list.append(price)
    
    if ctl.acc_vol >= ctl.vol_threshold:
        # Bar Logic
        o = ctl.acc_price_list[0]
        c = ctl.acc_price_list[-1]
        h = max(ctl.acc_price_list)
        l = min(ctl.acc_price_list)
        v_bar = ctl.acc_vol
        
        # ... Feature Construction (Same as class) ...
        # For brevity, reusing the logic from MaxwellController.on_tick
        # Ideally, MaxwellController.on_tick should take (price, vol) directly.
        # Let's assume we fixed MaxwellController above to take (tick, brain) 
        # but we pass a dummy object or change signature.
        
        # RE-IMPLEMENTING for clarity in this file:
        prev = ctl.prev_close if ctl.prev_close else o
        log_ret = np.log(c / (prev + 1e-9))
        ctl.prev_close = c
        
        log_vol = np.log1p(v_bar)
        volat = (h - l) / (o + 1e-9)
        mom = log_ret
        spread = 0.0
        
        features = np.array([log_ret, log_vol, volat, mom, spread])
        ctl.raw_bars.append(features)
        if len(ctl.raw_bars) > ctl.lookback: ctl.raw_bars.pop(0)
        
        ctl.acc_vol = 0.0
        ctl.acc_price_list = []
        
        if len(ctl.raw_bars) == ctl.lookback:
            tensor = np.array(ctl.raw_bars)
            S, E = brain.get_maxwell_state(tensor)
            gate = 1.0 / (1.0 + np.exp(ctl.gamma * (S - 0.5)))
            F = E * gate
            ctl.last_F = F
            return {'F': F, 'S': S, 'E': E}
            
    return None
