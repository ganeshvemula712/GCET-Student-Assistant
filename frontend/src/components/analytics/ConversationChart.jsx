import { useState } from "react";
import { TrendingUp } from "lucide-react";

export default function ConversationChart({ conversationsOverTime = [], messagesOverTime = [] }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  const dataLength = Math.max(conversationsOverTime.length, messagesOverTime.length, 1);
  const maxConv = Math.max(...conversationsOverTime.map((d) => d.count), 5);
  const maxMsg = Math.max(...messagesOverTime.map((d) => d.count), 5);
  const maxVal = Math.max(maxConv, maxMsg);

  // SVG dimensions
  const height = 220;
  const padding = 20;

  const pointsConv = conversationsOverTime.map((item, idx) => {
    const x = padding + (idx / Math.max(1, dataLength - 1)) * (600 - padding * 2);
    const y = height - padding - (item.count / maxVal) * (height - padding * 2);
    return { x, y, date: item.date, count: item.count };
  });

  const pointsMsg = messagesOverTime.map((item, idx) => {
    const x = padding + (idx / Math.max(1, dataLength - 1)) * (600 - padding * 2);
    const y = height - padding - (item.count / maxVal) * (height - padding * 2);
    return { x, y, date: item.date, count: item.count };
  });

  const pathConv = pointsConv.reduce(
    (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
    ""
  );

  const pathMsg = pointsMsg.reduce(
    (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
    ""
  );

  return (
    <div className="rounded-3xl border border-gray-800 bg-[#111827] p-6 shadow-xl space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp size={18} className="text-indigo-400" />
            <h3 className="text-base font-bold text-white">Conversation & Message Activity Trends</h3>
          </div>
          <p className="text-xs text-gray-400">Daily breakdown of student chat sessions and AI token response activity.</p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5 text-indigo-400">
            <span className="size-2.5 rounded-full bg-indigo-500" />
            <span>Conversations</span>
          </div>
          <div className="flex items-center gap-1.5 text-cyan-400">
            <span className="size-2.5 rounded-full bg-cyan-400" />
            <span>Messages</span>
          </div>
        </div>
      </div>

      {/* SVG Chart Container */}
      <div className="relative w-full overflow-hidden">
        <svg viewBox="0 0 600 240" className="w-full h-56 overflow-visible">
          {/* Background Grid Lines */}
          <line x1="20" y1="40" x2="580" y2="40" stroke="#1f2937" strokeDasharray="4 4" />
          <line x1="20" y1="100" x2="580" y2="100" stroke="#1f2937" strokeDasharray="4 4" />
          <line x1="20" y1="160" x2="580" y2="160" stroke="#1f2937" strokeDasharray="4 4" />
          <line x1="20" y1="200" x2="580" y2="200" stroke="#374151" />

          {/* Conversations Line Path */}
          {pointsConv.length > 1 && (
            <path d={pathConv} fill="none" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" />
          )}

          {/* Messages Line Path */}
          {pointsMsg.length > 1 && (
            <path d={pathMsg} fill="none" stroke="#22d3ee" strokeWidth="2.5" strokeDasharray="6 3" strokeLinecap="round" />
          )}

          {/* Data Points */}
          {pointsConv.map((p, idx) => (
            <g key={`conv-${idx}`}>
              <circle
                cx={p.x}
                cy={p.y}
                r="4"
                className="fill-indigo-500 stroke-gray-950 transition hover:r-6 cursor-pointer"
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              />
            </g>
          ))}

          {pointsMsg.map((p, idx) => (
            <g key={`msg-${idx}`}>
              <circle
                cx={p.x}
                cy={p.y}
                r="3.5"
                className="fill-cyan-400 stroke-gray-950 transition hover:r-6 cursor-pointer"
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              />
            </g>
          ))}
        </svg>

        {/* Interactive Hover Tooltip */}
        {hoveredIdx !== null && pointsConv[hoveredIdx] && (
          <div className="absolute top-2 right-4 rounded-2xl border border-gray-800 bg-gray-900/90 px-4 py-2.5 text-xs text-white shadow-2xl backdrop-blur-md">
            <p className="font-bold text-gray-300">{pointsConv[hoveredIdx].date}</p>
            <div className="mt-1 flex items-center gap-3">
              <span className="text-indigo-400 font-semibold">{pointsConv[hoveredIdx].count} Conversations</span>
              <span className="text-cyan-400 font-semibold">{pointsMsg[hoveredIdx]?.count || 0} Messages</span>
            </div>
          </div>
        )}
      </div>

      {/* Date Range Footer */}
      <div className="flex items-center justify-between border-t border-gray-800 pt-3 text-[11px] text-gray-500">
        <span>{conversationsOverTime.at(0)?.date || "Start"}</span>
        <span>Today ({conversationsOverTime.at(-1)?.date || "End"})</span>
      </div>
    </div>
  );
}
