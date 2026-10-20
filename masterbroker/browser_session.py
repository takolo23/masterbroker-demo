from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class IQOptionBrowserSession:
    """Stores the selected browser-session profile without passwords, cookies, or order privileges."""
    def __init__(self, path: Path): self.path = path
    def configure_demo(self, asset: str = 'EUR/USD', instrument: str = 'Blitz', expiry: str = '1 min', stake: float = 1.0) -> dict:
        if stake <= 0: raise ValueError('El monto virtual debe ser mayor que cero.')
        profile = {
            'platform': 'IQ Option',
            'connection': 'authenticated_browser_session',
            'account_mode': 'DEMO',
            'asset': asset,
            'instrument': instrument,
            'expiry': expiry,
            'virtual_stake': stake,
            'order_execution': 'DISABLED',
            'credentials_stored': False,
            'configured_at': datetime.now(timezone.utc).isoformat(),
            'note': 'La ejecuci�n de �rdenes permanece desactivada. Esta configuraci�n �nicamente identifica la sesi�n demo abierta por el usuario.'
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding='utf-8')
        return profile

