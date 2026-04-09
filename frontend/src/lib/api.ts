export type VehicleSpecs = {
  vin: string;
  make?: string | null;
  model?: string | null;
  year?: number | null;
  trim?: string | null;
  engine?: string | null;
  transmission?: string | null;
  country_of_origin?: string | null;
  safety_features: string[];
  source: "local" | "nhtsa" | "vindecoder" | "ai";
  confidence: number;
};

export type DecodeVinResponse = {
  specs: VehicleSpecs;
  raw: Record<string, unknown>;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function decodeVin(vin: string): Promise<DecodeVinResponse> {
  const r = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/decode-vin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vin })
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || `Request failed with status ${r.status}`);
  }
  return (await r.json()) as DecodeVinResponse;
}

