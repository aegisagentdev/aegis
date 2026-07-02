"""Runtime configuration for kabuto.

Values come from the environment (prefix ``KABUTO_``) or an ``.env`` file. Nothing
here is Robinhood-Chain-specific beyond sensible defaults; every network value can be
overridden so the scanner can be pointed at a fork, a testnet, or a different RPC.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KABUTO_", env_file=".env", extra="ignore")

    # --- Chain / RPC ---------------------------------------------------------
    # Robinhood Chain is an Arbitrum-Orbit L2. The public RPC + chain id must be
    # supplied by the operator; these defaults are placeholders and are validated
    # at startup (see `kabuto doctor`). Do not hardcode a guessed chain id into
    # signing logic — this tool never signs anyway, but be explicit.
    rpc_url: str = Field(
        default="https://rpc.robinhoodchain.example/placeholder",
        description="JSON-RPC HTTPS endpoint for Robinhood Chain.",
    )
    explorer_api: str = Field(
        default="https://robinhoodchain.blockscout.com/api",
        description="Blockscout-compatible explorer API base (used for verified-source checks).",
    )
    chain_id: int | None = Field(
        default=None, description="Expected chain id; if set, RPC eth_chainId is asserted against it."
    )

    # --- Scoring thresholds --------------------------------------------------
    # A verdict is NO-GO if the aggregate risk score reaches `nogo_score`, CAUTION
    # at `caution_score`, otherwise GO. Individual checks contribute points; see
    # kabuto.engine for how they combine.
    caution_score: int = Field(default=25, ge=0)
    nogo_score: int = Field(default=60, ge=0)

    # Pool depth: warn if the real reachable depth for the trade size is below this
    # fraction of the pool's nominal reserves.
    thin_depth_ratio: float = Field(default=0.35, ge=0.0, le=1.0)

    # LP concentration: flag if the top N holders control more than this fraction.
    concentration_top_n: int = Field(default=3, ge=1)
    concentration_flag_ratio: float = Field(default=0.80, ge=0.0, le=1.0)

    # Stock-token price divergence vs underlying reference (basis points).
    stock_divergence_warn_bps: int = Field(default=150, ge=0)
    stock_divergence_danger_bps: int = Field(default=500, ge=0)

    # --- AI layer ------------------------------------------------------------
    ai_enabled: bool = Field(default=True, description="Use Claude to summarize risk; falls back to a template.")
    ai_model: str = Field(default="claude-opus-4-8")
    request_timeout: float = Field(default=15.0, ge=1.0)


def load_settings() -> Settings:
    return Settings()
