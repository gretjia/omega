# Filename: rq/test_rq_strategy.py
import sys
# Add root to path so we can import rq
sys.path.append("d:/OMEGA")

from rq.interface import OmegaRQ

def main():
    print(">>> TESTING OMEGA RQ STRATEGY (v24 Maxwell) <<<")
    
    # 1. Init SDK
    OmegaRQ.init()
    
    # 2. Run Backtest
    # We rely on the default strategy loaded by runner
    # We need to make sure we have data for the test period
    # 000032.XSHE is in our bundle
    
    start_date = "2025-01-01"
    end_date = "2025-01-05"
    
    print(f"Running backtest from {start_date} to {end_date}...")
    
    try:
        results = OmegaRQ.alpha.run_backtest(
            start_date=start_date,
            end_date=end_date,
            capital=1000000
        )
        
        if results is not None:
            print("\n✅ Backtest Complete.")
            print("Summary:")
            # RQAlpha returns a dict or dataframe depending on config
            # 'sys_analyser' mod usually returns a result dict
            if 'sys_analyser' in results:
                summary = results['sys_analyser']['summary']
                print(f"Total Returns: {summary['total_returns']:.2%}")
                print(f"Annualized Returns: {summary['annualized_returns']:.2%}")
                print(f"Sharpe Ratio: {summary['sharpe']:.2f}")
                print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
            else:
                print("No summary available (check log level).")
        else:
            print("\n❌ Backtest returned None.")
            
    except Exception as e:
        print(f"\n❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
