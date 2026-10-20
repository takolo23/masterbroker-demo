from __future__ import annotations
import csv, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

class AlphaVantageForexSource:
    """Optional market-data fetcher. It reads only a local environment variable; it never sends orders."""
    def __init__(self, inbox: Path): self.inbox = inbox
    def fetch(self, from_symbol: str = 'EUR', to_symbol: str = 'USD', interval: str = '5min') -> Path:
        api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
        if not api_key: raise RuntimeError('Falta ALPHAVANTAGE_API_KEY. Config�rala localmente; no la pegues en el proyecto.')
        params = urlencode({'function':'FX_INTRADAY','from_symbol':from_symbol,'to_symbol':to_symbol,'interval':interval,'outputsize':'compact','datatype':'csv','apikey':api_key})
        with urlopen('https://www.alphavantage.co/query?'+params, timeout=30) as response:
            content = response.read().decode('utf-8')
        if not content.startswith('timestamp,'):
            raise RuntimeError('La fuente no devolvi� velas CSV v�lidas.')
        target = self.inbox / f'{from_symbol}{to_symbol}_{interval}.csv'
        self.inbox.mkdir(parents=True,exist_ok=True); target.write_text(content,encoding='utf-8')
        return target

