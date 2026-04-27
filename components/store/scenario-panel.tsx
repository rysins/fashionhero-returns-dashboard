"use client";

import { useMemo, useState } from "react";

import { useStore } from "@/components/store/store-provider";
import { interventionDefinitions, getSoftPenaltyEligibility } from "@/lib/data/preview-data";

export function ScenarioPanel() {
  const [open, setOpen] = useState(false);
  const { scenario, updateScenario } = useStore();
  const eligibility = getSoftPenaltyEligibility(scenario);
  const activeCount = useMemo(
    () =>
      [scenario.softPenaltyEnabled, scenario.dynamicCommissionEnabled, scenario.promoteLowReturnProductsEnabled].filter(Boolean)
        .length,
    [scenario],
  );

  return (
    <div className="fixed bottom-4 left-4 z-40 w-[320px] max-w-[calc(100vw-2rem)]">
      <button
        type="button"
        className="mb-2 rounded-full bg-charcoal px-4 py-2 text-xs font-medium uppercase tracking-[0.6px] text-white shadow-panel"
        onClick={() => setOpen((current) => !current)}
      >
        Preview Scenarios {activeCount > 0 ? `(${activeCount})` : ""}
      </button>
      {open ? (
        <div className="rounded-[24px] border border-black/10 bg-white p-4 shadow-panel">
          <div className="mb-3">
            <h2 className="text-sm font-semibold uppercase tracking-[0.5px] text-charcoal">Intervention preview</h2>
            <p className="mt-1 text-xs text-warm-gray">
              This panel changes storefront ranking, seller metadata and policy messaging without touching production logic.
            </p>
          </div>

          <div className="space-y-3">
            {interventionDefinitions.map((definition) => {
              const flagKey =
                definition.code === "soft_penalty_high_returners"
                  ? "softPenaltyEnabled"
                  : definition.code === "dynamic_commission_high_return_sellers"
                    ? "dynamicCommissionEnabled"
                    : "promoteLowReturnProductsEnabled";

              return (
                <label key={definition.code} className="flex items-start gap-3 rounded-2xl border border-black/5 bg-cream-light p-3">
                  <input
                    type="checkbox"
                    checked={scenario[flagKey]}
                    onChange={(event) => updateScenario({ [flagKey]: event.target.checked } as Partial<typeof scenario>)}
                  />
                  <span>
                    <span className="block text-sm font-medium text-charcoal">{definition.label}</span>
                    <span className="block text-xs text-warm-gray">Target: {definition.targetType}</span>
                  </span>
                </label>
              );
            })}
          </div>

          <div className="mt-4 rounded-2xl border border-black/5 p-3">
            <p className="mb-2 text-xs font-medium uppercase tracking-[0.5px] text-charcoal">Buyer preview cohort</p>
            <div className="mb-3 flex gap-2">
              {[
                { value: "baseline", label: "Baseline buyer" },
                { value: "high_returner", label: "High returner" },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`rounded-full border px-3 py-1.5 text-xs ${
                    scenario.currentBuyerProfile === option.value ? "border-charcoal bg-charcoal text-white" : "border-black/10"
                  }`}
                  onClick={() => updateScenario({ currentBuyerProfile: option.value as typeof scenario.currentBuyerProfile })}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <label className="block text-xs text-warm-gray">
              Returned orders this quarter: {scenario.quarterReturnsCount}
              <input
                type="range"
                min={0}
                max={6}
                step={1}
                value={scenario.quarterReturnsCount}
                onChange={(event) => updateScenario({ quarterReturnsCount: Number(event.target.value) })}
                className="mt-2 w-full"
              />
            </label>
            <p className={`mt-3 text-xs ${eligibility.qualifies ? "text-[#9e4040]" : "text-warm-gray"}`}>{eligibility.reason}</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
