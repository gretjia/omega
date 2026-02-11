from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Union

from .exceptions import QmtConnectionError, QmtNotInstalledError
from .utils import ensure_list, normalize_codes, normalize_code, to_timestr


class QmtDataClient:
    def __init__(
        self,
        port: int = 58610,
        reconnect_port: Optional[int] = None,
        enable_hello: bool = False,
        auto_connect: bool = True,
    ):
        self.port = int(port)
        self.reconnect_port = int(reconnect_port) if reconnect_port is not None else None
        self.enable_hello = bool(enable_hello)
        self._xtdata = None
        if auto_connect:
            self.connect()

    def _import_xtdata(self):
        if self._xtdata is not None:
            return self._xtdata
        try:
            from xtquant import xtdata
        except Exception as e:
            raise QmtNotInstalledError(
                "xtquant not available. Use QMT bundled Python or set PYTHONPATH to xtquant site-packages."
            ) from e
        try:
            xtdata.enable_hello = self.enable_hello
        except Exception:
            pass
        self._xtdata = xtdata
        return xtdata

    @property
    def xtdata(self):
        return self._import_xtdata()

    @property
    def data_dir(self) -> str:
        return getattr(self.xtdata, "data_dir", "")

    def connect(self) -> None:
        xtdata = self._import_xtdata()
        try:
            if self.reconnect_port is not None:
                xtdata.reconnect(port=self.reconnect_port)
            else:
                xtdata.connect(port=self.port)
        except Exception as e:
            raise QmtConnectionError(
                "Failed to connect to QMT xtquant service. Ensure QMT is running and logged in."
            ) from e

    def get_download_status(self) -> Any:
        return self.xtdata.get_download_status()

    def get_stock_list_in_sector(self, sector_name: str) -> List[str]:
        return list(self.xtdata.get_stock_list_in_sector(sector_name))

    def download_history_data(
        self,
        stock_code: str,
        period: str,
        start_time: Any,
        end_time: Any,
        incrementally: bool = True,
    ) -> Any:
        code = normalize_code(stock_code)
        return self.xtdata.download_history_data(
            code,
            period=period,
            start_time=to_timestr(start_time),
            end_time=to_timestr(end_time),
            incrementally=bool(incrementally),
        )

    def download_history_data2(
        self,
        stock_list: Union[str, Sequence[str]],
        period: str,
        start_time: Any,
        end_time: Any,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Any:
        codes = normalize_codes(stock_list)
        return self.xtdata.download_history_data2(
            stock_list=codes,
            period=period,
            start_time=to_timestr(start_time),
            end_time=to_timestr(end_time),
            callback=callback,
        )

    def get_market_data_ex(
        self,
        stock_list: Union[str, Sequence[str]],
        period: str,
        start_time: Any,
        end_time: Any,
        field_list: Optional[Iterable[str]] = None,
        dividend_type: Optional[str] = None,
        fill_data: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        codes = normalize_codes(stock_list)
        fields = ensure_list(field_list)
        params: Dict[str, Any] = dict(kwargs)
        if dividend_type is not None:
            params["dividend_type"] = dividend_type
        if fill_data is not None:
            params["fill_data"] = bool(fill_data)
        return self.xtdata.get_market_data_ex(
            fields,
            codes,
            period=period,
            start_time=to_timestr(start_time),
            end_time=to_timestr(end_time),
            **params,
        )

    def get_market_data(
        self,
        stock_list: Union[str, Sequence[str]],
        period: str,
        start_time: Any,
        end_time: Any,
        field_list: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        codes = normalize_codes(stock_list)
        fields = ensure_list(field_list)
        return self.xtdata.get_market_data(
            fields,
            codes,
            period=period,
            start_time=to_timestr(start_time),
            end_time=to_timestr(end_time),
            **kwargs,
        )

    def get_local_data(
        self,
        stock_list: Union[str, Sequence[str]],
        period: str,
        start_time: Any,
        end_time: Any,
        field_list: Optional[Iterable[str]] = None,
        data_dir: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        codes = normalize_codes(stock_list)
        fields = ensure_list(field_list)
        params: Dict[str, Any] = dict(kwargs)
        if data_dir is not None:
            params["data_dir"] = data_dir
        return self.xtdata.get_local_data(
            fields,
            codes,
            period=period,
            start_time=to_timestr(start_time),
            end_time=to_timestr(end_time),
            **params,
        )

    def get_price(
        self,
        order_book_ids: Union[str, Sequence[str]],
        start_date: Any,
        end_date: Any,
        frequency: str = "1d",
        fields: Optional[Iterable[str]] = None,
        adjust_type: Optional[str] = None,
        fill_data: bool = True,
    ) -> Any:
        dividend_type = None
        if adjust_type:
            at = str(adjust_type).lower()
            if at in ("pre", "front", "front_ratio"):
                dividend_type = "front_ratio"
            elif at in ("post", "back", "back_ratio"):
                dividend_type = "back_ratio"
            elif at in ("none", "raw"):
                dividend_type = None
        data = self.get_market_data_ex(
            stock_list=order_book_ids,
            period=frequency,
            start_time=start_date,
            end_time=end_date,
            field_list=fields,
            dividend_type=dividend_type,
            fill_data=fill_data,
        )
        if isinstance(order_book_ids, str):
            code = normalize_code(order_book_ids)
            return data.get(code)
        return data

    def get_ticks(
        self,
        order_book_ids: Union[str, Sequence[str]],
        start_dt: Any,
        end_dt: Any,
        kind: str = "tick",
        fields: Optional[Iterable[str]] = None,
    ) -> Any:
        data = self.get_market_data_ex(
            stock_list=order_book_ids,
            period=kind,
            start_time=start_dt,
            end_time=end_dt,
            field_list=fields,
        )
        if isinstance(order_book_ids, str):
            code = normalize_code(order_book_ids)
            return data.get(code)
        return data

    def get_full_tick(self, stock_list: Union[str, Sequence[str]]) -> Any:
        codes = normalize_codes(stock_list)
        return self.xtdata.get_full_tick(codes)

    def subscribe_quote(self, stock_code: str, period: str, callback: Callable[..., Any]) -> Any:
        code = normalize_code(stock_code)
        return self.xtdata.subscribe_quote(code, period=period, callback=callback)

