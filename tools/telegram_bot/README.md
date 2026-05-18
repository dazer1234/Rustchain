# RustChain Telegram Community Bot

Telegram bot for RustChain community chats. It answers the required bounty commands from live RustChain and wRTC endpoints, and keeps the existing alert and inline-query bonus features.

Issue: [rustchain-bounties#249](https://github.com/Scottcjn/rustchain-bounties/issues/249)

## Commands

| Command | Description |
| --- | --- |
| `/price` | wRTC price from Raydium via DexScreener. |
| `/miners` | Active miner list and count from `/api/miners`. |
| `/epoch` | Current epoch, slot, epoch pot, and enrolled miners. |
| `/balance <wallet>` | RTC balance from the configured RustChain balance node. |
| `/health` | Node health, version, uptime, DB status, and tip age. |
| `/subscribe` | Enable mining and price alerts in this chat. |
| `/unsubscribe` | Disable alerts in this chat. |

## Bonus Features

- Mining alerts for new miners and epoch changes.
- Price alerts when wRTC moves past `PRICE_CHANGE_THRESHOLD`.
- Inline queries for `price`, `miners`, and `epoch` after enabling inline mode in BotFather.

## Setup

```bash
cd tools/telegram_bot
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Create a bot with [@BotFather](https://t.me/BotFather), enable inline mode with `/setinline`, then edit `.env`:

```bash
TELEGRAM_BOT_TOKEN=123456:replace-me
RUSTCHAIN_API=https://explorer.rustchain.org
RTC_BALANCE_BASE=https://50.28.86.131
```

Run:

```bash
python telegram_bot.py
```

## Environment

| Variable | Default | Notes |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | required | Bot token from BotFather. |
| `RUSTCHAIN_API` | `https://explorer.rustchain.org` | Used for `/health`, `/miners`, and `/epoch`. |
| `RUSTCHAIN_API_BASE` | `https://explorer.rustchain.org` | Compatibility alias used by the local helper client. |
| `RTC_BALANCE_BASE` | `https://50.28.86.131` | Used for `/balance`; tries `/balance/<wallet>` then `/wallet/balance?miner_id=<wallet>`. |
| `PRICE_ALERT_INTERVAL` | `120` | Seconds between price checks. |
| `MINER_ALERT_INTERVAL` | `60` | Seconds between miner and epoch checks. |
| `PRICE_CHANGE_THRESHOLD` | `5.0` | Percent price move required for a price alert. |
| `WRTC_MINT` | canonical wRTC mint | Used by helper tests and Raydium links. |
| `WRTC_POOL_ID` | canonical pool id | Used by helper tests and Raydium links. |
| `WRTC_SWAP_URL` | Raydium swap URL | Used by helper tests and Raydium links. |
| `WRTC_PRICE_API` | empty | Optional JSON quote endpoint for the local helper client. |
| `REQUEST_TIMEOUT_SECONDS` | `15` | HTTP timeout for the local helper client. |

## Deployment

Systemd example:

```ini
[Unit]
Description=RustChain Telegram Bot
After=network-online.target

[Service]
WorkingDirectory=/opt/Rustchain/tools/telegram_bot
EnvironmentFile=/opt/Rustchain/tools/telegram_bot/.env
ExecStart=/opt/Rustchain/tools/telegram_bot/.venv/bin/python telegram_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Docker remains supported by the existing `Dockerfile`:

```bash
docker build -t rustchain-tg-bot .
docker run --env-file .env rustchain-tg-bot
```

## Safety

- The bot is read-only.
- It never asks for seed phrases, private keys, Telegram passwords, or GitHub tokens.
- `/balance` accepts a public wallet or miner id only.
- `/price` is informational and does not execute swaps.

## Local Tests

From the repository root:

```bash
python -m py_compile tools/telegram_bot/api_client.py tools/telegram_bot/telegram_bot.py tools/telegram_bot/test_api_client.py
python -m unittest tools.telegram_bot.test_api_client
```
