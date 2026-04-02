"use client";
import { useEffect, useState } from "react";
import type { CartographyData } from "./types";

export function useCartographyData() {
  const [data, setData] = useState<CartographyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/cartography")
      .then((r) => r.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  return { data, loading, error };
}
