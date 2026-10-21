import json
import shutil
import unittest
from datetime import date
from pathlib import Path

from masterbroker.config import RiskConfig
from masterbroker.iqoption_adapter import IQOptionAdapter
from masterbroker.learner_agent import LearningAgent
from masterbroker.risk import RiskEngine
from run_demo import synthetic

class MasterBrokerTests(unittest.TestCase):
    def test_risk_circuit_breaks_after_three_losses(self):
        engine = RiskEngine(RiskConfig(daily_loss_limit=1.0, max_consecutive_losses=3, max_trades_per_day=10))
        today = date(2026, 1, 1)
        for _ in range(3):
            self.assertTrue(engine.can_trade(today)[0])
            engine.record(-1.0)
        allowed, reason = engine.can_trade(today)
        self.assertFalse(allowed)
        self.assertIn('racha m�xima', reason)

    def test_learning_keeps_append_only_ledger(self):
        folder = Path(__file__).parent / '_sandbox_test_memory'
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir()
        try:
            agent = LearningAgent(folder / 'model_registry.json')
            state = agent.learn(synthetic(), 'test-data')
            ledger = folder / 'learning_ledger.jsonl'
            self.assertTrue(ledger.exists())
            entries = [json.loads(line) for line in ledger.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['mode'], 'PAPER_TRADING_ONLY')
            self.assertEqual(state['mode'], 'PAPER_TRADING_ONLY')
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_real_execution_adapter_is_blocked(self):
        with self.assertRaises(RuntimeError):
            IQOptionAdapter().place_order('EURUSD', 'LONG', 1)

    def test_browser_profile_is_demo_and_order_execution_is_disabled(self):
        from masterbroker.browser_session import IQOptionBrowserSession
        folder = Path(__file__).parent / '_sandbox_test_browser'
        shutil.rmtree(folder, ignore_errors=True); folder.mkdir()
        try:
            profile = IQOptionBrowserSession(folder / 'session.json').configure_demo()
            self.assertEqual(profile['account_mode'], 'DEMO')
            self.assertEqual(profile['order_execution'], 'DISABLED')
            self.assertFalse(profile['credentials_stored'])
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_service_writes_demo_status_without_orders(self):
        import agent_service
        status = agent_service.run_cycle()
        self.assertEqual(status['mode'], 'DEMO_ONLY')
        self.assertEqual(status['live_orders'], 'DISABLED')

    def test_news_filter_pauses_on_high_impact_note(self):
        from masterbroker.alerting import NewsSafetyFilter
        folder = Path(__file__).parent / '_sandbox_test_alert'
        shutil.rmtree(folder, ignore_errors=True); folder.mkdir()
        try:
            note = folder / 'note.md'; note.write_text('Upcoming FOMC interest rate decision', encoding='utf-8')
            result = NewsSafetyFilter(folder / 'alerts.jsonl').assess(note)
            self.assertEqual(result['level'], 'PAUSE')
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_agent_team_blocks_low_confidence_and_stays_demo_only(self):
        from masterbroker.agents import evaluate_team
        team = evaluate_team({'action':'ALERT_ONLY','side':'LONG','score':.60,'reason':'test'}, {'confidence':85,'onlyAnalyze':False,'askConfirm':True})
        self.assertEqual(team['mode'], 'DEMO_ONLY')
        self.assertEqual(team['live_orders'], 'DISABLED')
        self.assertEqual(team['proposal'], 'NO_OPERAR')
        self.assertEqual(len(team['agents']), 4)

if __name__ == '__main__':
    unittest.main()

