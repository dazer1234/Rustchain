import unittest
from unittest.mock import Mock

from tools.telegram_bot.api_client import RustChainAPI, miner_family_counts, normalize_miners


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self):
        return self._payload


class TelegramBotApiClientTests(unittest.TestCase):
    def test_normalize_miners_supports_wrapped_payload(self):
        payload = {"miners": [{"device_family": "PowerPC"}]}
        self.assertEqual(normalize_miners(payload), [{"device_family": "PowerPC"}])

    def test_miner_family_counts_sorts_by_count(self):
        miners = [
            {"device_family": "PowerPC"},
            {"device_family": "PowerPC"},
            {"hardware_type": "Unknown/Other"},
        ]
        self.assertEqual(miner_family_counts(miners), {"PowerPC": 2, "Unknown/Other": 1})

    def test_balance_falls_back_to_wallet_balance_endpoint(self):
        session = Mock()
        session.get.side_effect = [
            FakeResponse({"error": "not found"}, 404),
            FakeResponse({"balance": 7.5}, 200),
        ]
        api = RustChainAPI(api_base="https://api.example", balance_base="https://node.example", session=session)

        self.assertEqual(api.balance("miner1"), {"balance": 7.5})
        self.assertEqual(session.get.call_count, 2)
        self.assertIn("/wallet/balance", session.get.call_args[0][0])

    def test_price_without_quote_returns_raydium_links(self):
        api = RustChainAPI(session=Mock())
        data = api.price()
        self.assertIn("mint", data)
        self.assertIn("swap_url", data)
        self.assertIn("No WRTC_PRICE_API configured", data["message"])


if __name__ == "__main__":
    unittest.main()
