from xtquant import xtdata
import time

port = 58610
xtdata.connect(port=port)

code = "000559.SZ"
# check_download_status is a common way to see if data is ready
# but let's just try to get a count of what's in local cache right now
start = "20240101"
end = "20260122"

print(f"Checking local cache for {code} from {start} to {end}...")
res = xtdata.get_market_data_ex(stock_list=[code], period="tick", start_time=start, end_time=end)
if code in res:
    print(f"Current rows in local cache: {len(res[code])}")
    if not res[code].empty:
        print(f"Cache Range: {res[code]['time'].min()} to {res[code]['time'].max()}")
else:
    print("Stock not in result.")

# Check if there's any active download
try:
    status = xtdata.get_download_status()
    print("General Download Status:", status)
except Exception as e:
    print("Could not get download status:", e)
