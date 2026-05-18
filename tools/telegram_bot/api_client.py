from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests

DEFAULT_API_BASE = "https://explorer.rustchain.org"
DEFAULT_BALANCE_BASE = "https://50.28.86.131"
DEFAULT_WRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"
DEFAULT_WRTC_POOL_ID = "8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb"
DEFAULT_WRTC_SWAP_URL = (
    "https://raydium.io/swap/?inputMint=sol&outputMint="
    "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"
)


@dataclass
class RustChainAPI:
    api_base: str = DEFAULT_API_BASE
    balance_base: str = DEFAULT_BALANCE_BASE
    timeout: int = 15
    session: requests.Session = field(default_factory=requests.Session)

    @classmethod
    def from_env(cls) -> "RustChainAPI":
        return cls(
            api_base=os.environ.get("RUSTCHAIN_API_BASE", DEFAULT_API_BASE).rstrip("/"),
            balance_base=os.environ.get("RTC_BALANCE_BASE", DEFAULT_BALANCE_BASE).rstrip("/"),
            timeout=int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15")),
        )

    def get_json(self, base: str, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        response = self.session.get(f"{base}{path}", params=params or {}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        return self.get_json(self.api_base, "/health")

    def miners(self) -> Dict[str, Any]:
        return self.get_json(self.api_base, "/api/miners")

    def epoch(self) -> Dict[str, Any]:
        return self.get_json(self.api_base, "/epoch")

    def balance(self, wallet: str) -> Dict[str, Any]:
        try:
            return self.get_json(self.balance_base, f"/balance/{wallet}")
        except requests.HTTPError:
            return self.get_json(self.balance_base, "/wallet/balance", {"miner_id": wallet})

    def price(self) -> Dict[str, Any]:
        price_api = os.environ.get("WRTC_PRICE_API", "").strip()
        payload: Dict[str, Any] = {
            "mint": os.environ.get("WRTC_MINT", DEFAULT_WRTC_MINT),
            "pool_id": os.environ.get("WRTC_POOL_ID", DEFAULT_WRTC_POOL_ID),
            "swap_url": os.environ.get("WRTC_SWAP_URL", DEFAULT_WRTC_SWAP_URL),
        }
        if not price_api:
            payload["message"] = "No WRTC_PRICE_API configured; use Raydium pool/swap links for live price."
            return payload
        response = self.session.get(price_api, timeout=self.timeout)
        response.raise_for_status()
        quote = response.json()
        payload["quote"] = quote
        return payload


def normalize_miners(payload: Dict[str, Any]) -> list[Dict[str, Any]]:
    miners = payload.get("miners", payload if isinstance(payload, list) else [])
    return miners if isinstance(miners, list) else []


def miner_family_counts(miners: list[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for miner in miners:
        family = str(miner.get("device_family") or miner.get("hardware_type") or "Unknown")
        counts[family] = counts.get(family, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
