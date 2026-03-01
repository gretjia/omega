from xtquant import xtdata
import time

port = 58610
print(f"Connecting to QMT on port {port}...")
xtdata.connect(port=port)
print("Connected. Waiting 10 seconds for data service to initialize...")
time.sleep(10)

code = "000559.SZ"
start = "20260120"
end = "20260121"

print(f"Attempting to download {code} from {start} to {end}...")
try:
    xtdata.download_history_data(code, period="tick", start_time=start, end_time=end)
    print("Download command sent.")
    time.sleep(2)
    res = xtdata.get_market_data_ex(stock_list=[code], period="tick", start_time=start, end_time=end)
    if code in res and not res[code].empty:
        print(f"Success! Retrieved {len(res[code])} rows.")
    else:
        print("Failed to retrieve data. Result is empty.")
except Exception as e:
    print(f"Error during download: {e}")
