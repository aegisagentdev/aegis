// Aegis mark — the official trefoil-knot logo (transparent PNG, glow baked in).
/* eslint-disable @next/next/no-img-element */

export function Logo({ size = 22 }: { size?: number }) {
  return (
    <img
      src="/aegis-logo.png"
      alt="Aegis"
      width={size}
      height={size}
      style={{ display: "block", objectFit: "contain" }}
    />
  );
}
