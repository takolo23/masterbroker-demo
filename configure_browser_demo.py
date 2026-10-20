from pathlib import Path
from masterbroker.browser_session import IQOptionBrowserSession

if __name__ == '__main__':
    root = Path(__file__).parent
    profile = IQOptionBrowserSession(root / 'reports' / 'browser_connection.json').configure_demo()
    print(f"Session set: {profile['account_mode']} | {profile['asset']} {profile['instrument']} | {profile['expiry']} | ${profile['virtual_stake']:.2f}")

