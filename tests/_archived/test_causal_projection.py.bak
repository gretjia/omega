
import unittest
import polars as pl
import numpy as np
import os
import sys
from dataclasses import replace

# Add project root to path
sys.path.append(os.getcwd())

from config import L2PipelineConfig
from omega_core.omega_etl import build_l2_frames

class TestCausalProjection(unittest.TestCase):
    def test_dynamic_bucket_calculation(self):
        cfg = L2PipelineConfig()
        
        # Update Mapping to match English columns
        mapping_new = replace(cfg.mapping, 
                              col_time="time", 
                              col_price="price", 
                              col_volume="vol",
                              col_date="date",
                              col_turnover="turnover",
                              col_bs_flag="bs_flag",
                              bid_price_prefix="bid_p",
                              bid_volume_prefix="bid_v",
                              ask_price_prefix="ask_p",
                              ask_volume_prefix="ask_v",
                              book_levels=1)
        
        vc_new = replace(cfg.volume_clock, 
                         dynamic_bucket_size=True, 
                         daily_volume_proxy_div=100.0, 
                         min_ticks_per_bucket=1)
        
        io_new = replace(cfg.io, input_format="csv", csv_encoding="utf8")
        
        cfg = replace(cfg, mapping=mapping_new, volume_clock=vc_new, io=io_new)
        
        start_time = int(cfg.session.session_1_start)
        total_duration = int(cfg.session.session_2_end) - start_time
        target_time = start_time + int(0.1 * total_duration)
        
        data = {
            "time": [start_time + 60000, target_time], 
            "price": [10.0, 10.1],
            "vol": [5000.0, 5000.0], 
            "bid_p1": [9.9, 10.0],
            "ask_p1": [10.1, 10.2],
            "bid_v1": [100.0, 100.0],
            "ask_v1": [100.0, 100.0],
            "turnover": [50000.0, 50500.0],
            "bs_flag": [1.0, 1.0],
            "date": ["20240201", "20240201"]
        }
        
        df = pl.DataFrame(data)
        temp_csv = "tests/mock_data.csv"
        df.write_csv(temp_csv)
        
        try:
            result_df = build_l2_frames(temp_csv, cfg, target_frames=100)
            self.assertGreater(result_df.height, 0, "Should have produced at least one frame")
            print("Causal Projection Result Frame:")
            print(result_df)
            
        finally:
            if os.path.exists(temp_csv):
                os.remove(temp_csv)

if __name__ == "__main__":
    unittest.main()
