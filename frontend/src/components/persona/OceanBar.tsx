import { OceanScores } from "@/types";

const TRAITS = [
  { key: "openness" as const, label: "Openness", color: "bg-purple-500" },
  { key: "conscientiousness" as const, label: "Conscientiousness", color: "bg-blue-500" },
  { key: "extraversion" as const, label: "Extraversion", color: "bg-amber-500" },
  { key: "agreeableness" as const, label: "Agreeableness", color: "bg-emerald-500" },
  { key: "neuroticism" as const, label: "Neuroticism", color: "bg-red-500" },
];

interface OceanBarProps {
  scores: OceanScores;
}

export function OceanBar({ scores }: OceanBarProps) {
  return (
    <div className="space-y-2">
      {TRAITS.map(({ key, label, color }) => {
        const pct = Math.round(scores[key] * 100);
        return (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-300 font-medium">{label}</span>
              <span className="text-gray-500 dark:text-gray-400">{pct}%</span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                className={`h-full ${color} rounded-full transition-all`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
