"""Runtime configuration for aegis.

Values come from the environment (prefix ``AEGIS_``) or an ``.env`` file. Nothing
here is Robinhood-Chain-specific beyond sensible defaults; every network value can be
overridden so the scanner can be pointed at a fork, a testnet, or a different RPC.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGIS_", env_file=".env", extra="ignore")

    # --- Chain / RPC ---------------------------------------------------------
    # Robinhood Chain is an Arbitrum-Orbit L2 (mainnet chain id 4663, ETH gas).
    # The default public RPC is keyless and rate-limited — fine for a pre-trade
    # scanner's light read calls; point at Alchemy/dRPC for heavy use. Validated
    # at startup via `aegis doctor`.
    rpc_url: str = Field(
        default="https://rpc.mainnet.chain.robinhood.com",
        description="JSON-RPC HTTPS endpoint for Robinhood Chain.",
    )
    explorer_api: str = Field(
        default="https://robinhoodchain.blockscout.com/api",
        description="Blockscout-compatible explorer API base (used for verified-source checks).",
    )
    chain_id: int | None = Field(
        default=4663, description="Expected chain id; if set, RPC eth_chainId is asserted against it."
    )

    # --- Scoring thresholds --------------------------------------------------
    # A verdict is NO-GO if the aggregate risk score reaches `nogo_score`, CAUTION
    # at `caution_score`, otherwise GO. Individual checks contribute points; see
    # aegis.engine for how they combine.
    caution_score: int = Field(default=25, ge=0)
    nogo_score: int = Field(default=60, ge=0)

    # Pool depth: warn if the real reachable depth for the trade size is below this
    # fraction of the pool's nominal reserves.
    thin_depth_ratio: float = Field(default=0.35, ge=0.0, le=1.0)

    # --- Young-chain leniency ------------------------------------------------
    # A freshly-launched chain legitimately has thin books, low volume and no
    # trading history, so *market-maturity* signals should caution rather than
    # hard-block. These knobs relax only those signals; security signals
    # (honeypot, hidden fee, mint, owner permissions) still block on any chain.
    # Defaults are strict (mature-chain); the CLI relaxes them for Robinhood
    # Chain, and --strict / --lenient override per run.
    liq_danger_below: int = Field(default=5_000, ge=0)  # very-thin liquidity cutoff (USD)
    liq_warn_below: int = Field(default=25_000, ge=0)  # low-liquidity cutoff (USD)
    block_on_thin_liquidity: bool = Field(default=True)  # thin book -> NO-GO (else CAUTION)
    block_on_high_impact: bool = Field(default=True)  # oversized trade -> NO-GO (else CAUTION)

    # LP concentration: flag if the top N holders control more than this fraction.
    concentration_top_n: int = Field(default=3, ge=1)
    concentration_flag_ratio: float = Field(default=0.80, ge=0.0, le=1.0)

    # Stock-token price divergence vs underlying reference (basis points).
    stock_divergence_warn_bps: int = Field(default=150, ge=0)
    stock_divergence_danger_bps: int = Field(default=500, ge=0)

    # --- External data sources -----------------------------------------------
    # GoPlus Security provides a free, keyless second opinion (honeypot, tax,
    # admin permissions). It is chain-scoped: set goplus_chain_id to a supported
    # EVM chain id (1 = Ethereum, 8453 = Base, 42161 = Arbitrum, ...) to enable
    # enrichment. Left as None, the scanner runs on-chain checks only.
    goplus_enabled: bool = Field(default=True, description="Enrich findings with GoPlus token-security data.")
    goplus_chain_id: int | None = Field(default=None, description="EVM chain id to query GoPlus against.")

    # DexScreener provides live market data (price, liquidity, volume) and covers
    # Robinhood Chain (slug "robinhood") where GoPlus does not. Set the slug to
    # enable market enrichment.
    dexscreener_enabled: bool = Field(default=True, description="Enrich findings with DexScreener market data.")
    dexscreener_chain: str | None = Field(default=None, description="DexScreener chain slug to query.")

    # --- AI layer ------------------------------------------------------------
    ai_enabled: bool = Field(default=True, description="Use Claude to summarize risk; falls back to a template.")
    ai_model: str = Field(default="claude-opus-4-8")
    request_timeout: float = Field(default=15.0, ge=1.0)


def load_settings() -> Settings:
    return Settings()
