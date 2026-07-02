"""Show how to configure Hood Trade programmatically."""

from hoodtrade.config import Settings

settings = Settings(
    rpc_url="https://rpc.robinhoodchain.com",
    chain_id=42161,
    caution_score=20,
    nogo_score=50,
    ai_enabled=True,
    ai_model="claude-opus-4-8",
)

print(f"RPC:      {settings.rpc_url}")
print(f"Chain:    {settings.chain_id}")
print(f"Caution:  {settings.caution_score}")
print(f"No-Go:    {settings.nogo_score}")
print(f"AI:       {'on' if settings.ai_enabled else 'off'}")
