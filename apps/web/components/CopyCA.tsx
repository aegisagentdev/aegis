"use client";

import { useState } from "react";

export default function CopyCA({ address }: { address: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="copy-btn"
      onClick={() => {
        navigator.clipboard?.writeText(address).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1400);
        });
      }}
    >
      {copied ? "copied ✓" : "copy"}
    </button>
  );
}
