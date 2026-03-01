from qmt import api
from qmt.exceptions import QmtError


def main():
    try:
        api.init(port=58610, enable_hello=False, auto_connect=True)
        print("Connected. data_dir:", api.data.data_dir)

        code = "000001.SZ"
        df = api.data.get_price(code, start_date="20250102", end_date="20250103", frequency="1d")
        if df is None:
            print("No result for", code)
        else:
            print("Rows:", len(df))
            print(df.head())
    except QmtError as e:
        print("QMT error:", e)


if __name__ == "__main__":
    main()

