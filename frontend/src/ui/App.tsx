import { useMemo, useState } from "react";
import { decodeVin, type VehicleSpecs } from "../lib/api";

function classNames(...xs: Array<string | false | undefined>) {
  return xs.filter(Boolean).join(" ");
}

function SpecCard(props: { title: string; value?: string | number | null }) {
  return (
    <div className="rounded-2xl bg-white shadow-soft border border-slate-100 p-4">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{props.title}</div>
      <div className="mt-2 text-lg font-semibold text-slate-900">{props.value ?? "—"}</div>
    </div>
  );
}

export default function App() {
  const [vin, setVin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [specs, setSpecs] = useState<VehicleSpecs | null>(null);

  const imageUrl = useMemo(() => {
    const seed = (specs?.vin ?? vin).trim() || "vehicle";
    return `https://picsum.photos/seed/${encodeURIComponent(seed)}/1200/520`;
  }, [specs?.vin, vin]);

  async function onDecode() {
    setError(null);
    setSpecs(null);
    const v = vin.trim().toUpperCase();
    setVin(v);
    if (v.length !== 17) {
      setError("VIN must be exactly 17 characters.");
      return;
    }
    setLoading(true);
    try {
      const res = await decodeVin(v);
      setSpecs(res.specs);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="mx-auto max-w-6xl px-4 py-10">
          <div className="flex items-center justify-between gap-6 flex-wrap">
            <div>
              <div className="text-sm font-semibold text-slate-200">AutoVIN Intelligence System</div>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">VIN Decode Dashboard</h1>
              <p className="mt-2 text-slate-200 max-w-2xl">
                Enter a VIN to retrieve make/model/year, configuration, engine & transmission details, origin, and safety
                signals. Results are cached and rate-limited.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <input
                value={vin}
                onChange={(e) => setVin(e.target.value)}
                placeholder="Enter 17-character VIN"
                className="w-[320px] max-w-[70vw] rounded-xl px-4 py-3 text-slate-900 outline-none ring-1 ring-slate-300 focus:ring-2 focus:ring-indigo-400"
              />
              <button
                onClick={onDecode}
                disabled={loading}
                className={classNames(
                  "rounded-xl px-5 py-3 font-semibold",
                  loading ? "bg-slate-500 cursor-not-allowed" : "bg-indigo-500 hover:bg-indigo-600"
                )}
              >
                {loading ? "Decoding..." : "Decode"}
              </button>
            </div>
          </div>

          {error ? (
            <div className="mt-6 rounded-xl bg-red-500/15 border border-red-500/30 px-4 py-3 text-red-100">
              <div className="font-semibold">Error</div>
              <div className="mt-1 text-sm opacity-95">{error}</div>
            </div>
          ) : null}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="rounded-3xl overflow-hidden shadow-soft border border-slate-100 bg-white">
          <img src={imageUrl} alt="Vehicle" className="h-[240px] w-full object-cover" />
          <div className="p-5 flex items-center justify-between gap-4 flex-wrap">
            <div>
              <div className="text-sm text-slate-500">Vehicle</div>
              <div className="text-2xl font-bold">
                {specs?.year ?? "—"} {specs?.make ?? "—"} {specs?.model ?? ""}
              </div>
              <div className="mt-1 text-sm text-slate-600">
                VIN: {(specs?.vin ?? vin.trim().toUpperCase()) || "—"}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-slate-100 px-3 py-2 text-sm">
                <span className="font-semibold">Source:</span> {specs?.source ?? "—"}
              </div>
              <div className="rounded-xl bg-slate-100 px-3 py-2 text-sm">
                <span className="font-semibold">Confidence:</span>{" "}
                {specs ? `${Math.round(specs.confidence * 100)}%` : "—"}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <SpecCard title="Trim / Configuration" value={specs?.trim} />
          <SpecCard title="Engine" value={specs?.engine} />
          <SpecCard title="Transmission" value={specs?.transmission} />
          <SpecCard title="Country of Origin" value={specs?.country_of_origin} />
          <SpecCard title="Safety Features" value={specs?.safety_features?.join(", ") || null} />
          <SpecCard title="Cache / Rate Limit" value="Enabled" />
        </div>

        <div className="mt-10 rounded-2xl bg-white border border-slate-100 shadow-soft p-5">
          <div className="text-lg font-bold">Notes</div>
          <ul className="mt-2 list-disc pl-5 text-slate-700 space-y-1">
            <li>NHTSA is used first when available; external decoder + AI estimation fill gaps.</li>
            <li>Car image uses a public placeholder service seeded by VIN.</li>
            <li>Optional recall/accident history hooks are included in the API shape for future integrations.</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

