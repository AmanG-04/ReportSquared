import { useState } from "react";
import { motion } from "motion/react";
import { ArrowLeft, TrendingUp, TrendingDown } from "lucide-react";
import { LineChart, Line, Tooltip, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import { StockData } from "../services/api";

interface StockPageProps {
  stock: StockData;
  onBack: () => void;
}

export function StockPage({ stock, onBack }: StockPageProps) {
  const isPositive = stock.priceChange >= 0;
  const normalizedDailyHistory = (stock.historicalOHLCV || [])
    .map((point) => {
      const toFinite = (value: number | null | undefined) => {
        if (value === null || value === undefined) return null;
        const num = Number(value);
        return Number.isFinite(num) ? num : null;
      };

      return {
        ...point,
        open: toFinite(point.open),
        high: toFinite(point.high),
        low: toFinite(point.low),
        close: toFinite(point.close),
        adjClose: toFinite(point.adjClose),
        volume: toFinite(point.volume),
        price: toFinite(point.close) ?? toFinite(point.adjClose) ?? toFinite(point.open),
      };
    })
    .filter((point) => point.price !== null);

  const chartDailyHistory = normalizedDailyHistory.slice(-180);

  const hasDailyHistory = chartDailyHistory.length > 0;
  const surfaceStyle = {
    background: "linear-gradient(180deg, rgba(95,104,115,0.92) 0%, rgba(79,87,98,0.92) 100%)",
    border: "1px solid rgba(255,255,255,0.08)",
    boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
    backdropFilter: "blur(6px)",
  } as const;

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          whileHover={{ x: -5 }}
          onClick={onBack}
          className="flex items-center gap-2 mb-8 px-4 py-2 rounded-lg transition-all"
          style={{ color: "#3E8EDE" }}
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to search</span>
        </motion.button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 rounded-3xl p-6"
          style={surfaceStyle}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h1 className="text-5xl tracking-tight">{stock.symbol}</h1>
              {isPositive ? (
                <TrendingUp className="w-8 h-8" style={{ color: "#4ADE80" }} />
              ) : (
                <TrendingDown className="w-8 h-8" style={{ color: "#F87171" }} />
              )}
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold">Rs. {stock.currentPrice.toFixed(2)}</p>
              <div className="flex items-center gap-2 justify-end">
                <span
                  className="text-lg font-semibold"
                  style={{ color: isPositive ? "#4ADE80" : "#F87171" }}
                >
                  {isPositive ? "+" : ""}Rs. {stock.priceChange.toFixed(2)}
                </span>
                <span
                  className="text-lg"
                  style={{ color: isPositive ? "#4ADE80" : "#F87171" }}
                >
                  ({isPositive ? "+" : ""}{stock.priceChangePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
          <p className="text-xl opacity-60" style={{ color: "#B8BCC1" }}>
            {stock.name}
          </p>
        </motion.div>

        {/* Daily OHLCV History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.08 }}
          className="mb-6 rounded-3xl p-6"
          style={surfaceStyle}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl">Daily Price History (OHLCV)</h3>
            {hasDailyHistory && (
              <p className="text-sm opacity-70" style={{ color: "#B8BCC1" }}>
                {chartDailyHistory.length} trading days
              </p>
            )}
          </div>

          {!hasDailyHistory ? (
            <p className="text-sm opacity-70" style={{ color: "#B8BCC1" }}>
              No daily market history found for this symbol.
            </p>
          ) : (
            <>
              <div className="mb-6">
                <SimplePriceChart data={chartDailyHistory} />
              </div>

              <div>
                <SimpleVolumeChart data={chartDailyHistory} />
              </div>

              <div className="mt-4 flex flex-wrap gap-2 text-xs" style={{ color: "#D9DDE1" }}>
                <span className="px-3 py-1.5 rounded-full" style={{ backgroundColor: "rgba(245,158,11,0.16)", border: "1px solid rgba(245,158,11,0.35)" }}>Open</span>
                <span className="px-3 py-1.5 rounded-full" style={{ backgroundColor: "rgba(74,222,128,0.15)", border: "1px solid rgba(74,222,128,0.35)" }}>High</span>
                <span className="px-3 py-1.5 rounded-full" style={{ backgroundColor: "rgba(248,113,113,0.15)", border: "1px solid rgba(248,113,113,0.35)" }}>Low</span>
                <span className="px-3 py-1.5 rounded-full" style={{ backgroundColor: "rgba(62,142,222,0.16)", border: "1px solid rgba(62,142,222,0.35)" }}>Close</span>
                <span className="px-3 py-1.5 rounded-full" style={{ backgroundColor: "rgba(124,155,193,0.18)", border: "1px solid rgba(124,155,193,0.35)" }}>Volume</span>
              </div>
            </>
          )}
        </motion.div>

        {/* Key Metrics Summary Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: "1rem",
          }}
        >
          {stock.ebitdaMargin !== undefined && (
            <div className="rounded-2xl p-4 overflow-hidden text-center" style={surfaceStyle}>
              <p className="text-xs uppercase tracking-wide opacity-70 mb-1 truncate">EBITDA Margin</p>
              <p className="text-[2rem] leading-none font-bold truncate">{stock.ebitdaMargin?.toFixed(2)}%</p>
            </div>
          )}
          {stock.netProfitMargin !== undefined && (
            <div className="rounded-2xl p-4 overflow-hidden text-center" style={surfaceStyle}>
              <p className="text-xs uppercase tracking-wide opacity-70 mb-1 truncate">Net Profit Margin</p>
              <p className="text-[2rem] leading-none font-bold truncate">{stock.netProfitMargin?.toFixed(2)}%</p>
            </div>
          )}
          {stock.eps?.current !== undefined && (
            <div className="rounded-2xl p-4 overflow-hidden text-center" style={surfaceStyle}>
              <p className="text-xs uppercase tracking-wide opacity-70 mb-1 truncate">EPS (Current)</p>
              <p className="text-[2rem] leading-none font-bold truncate">Rs. {stock.eps.current?.toFixed(2)}</p>
            </div>
          )}
          {stock.cashFlow?.current !== undefined && (
            <div className="rounded-2xl p-4 overflow-hidden text-center" style={surfaceStyle}>
              <p className="text-xs uppercase tracking-wide opacity-70 mb-1 truncate">Cash Flow (Cr)</p>
              <p className="text-[2rem] leading-none font-bold truncate">{(stock.cashFlow.current / 100).toFixed(0)}</p>
            </div>
          )}
        </motion.div>

        {/* Main Financial Metrics Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <MetricCard
            title="Revenue Growth %"
            qoqData={stock.revenue.qoq}
            yoyData={stock.revenue.yoy}
            delay={0.2}
            color="#3E8EDE"
          />
          <MetricCard
            title="Net Profit Growth %"
            qoqData={stock.netProfit.qoq}
            yoyData={stock.netProfit.yoy}
            delay={0.3}
            color="#8B5CF6"
          />
          <MetricCard
            title="EBITDA Growth %"
            qoqData={stock.ebitda.qoq}
            yoyData={stock.ebitda.yoy}
            delay={0.4}
            color="#10B981"
          />
          {stock.eps?.qoqChange !== undefined && stock.eps?.yoyChange !== undefined && (
            <div className="rounded-3xl p-6" style={surfaceStyle}>
              <h3 className="text-2xl mb-4">EPS Changes</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm opacity-60">Current EPS</p>
                  <p className="text-3xl font-bold">Rs. {stock.eps.current?.toFixed(2)}</p>
                </div>
                <div className="flex justify-between">
                  <div>
                    <p className="text-xs opacity-60">QoQ Change</p>
                    <p className="text-xl" style={{ color: (stock.eps.qoqChange || 0) >= 0 ? "#4ADE80" : "#F87171" }}>
                      {(stock.eps.qoqChange || 0) >= 0 ? "+" : ""}{stock.eps.qoqChange?.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs opacity-60">YoY Change</p>
                    <p className="text-xl" style={{ color: (stock.eps.yoyChange || 0) >= 0 ? "#4ADE80" : "#F87171" }}>
                      {(stock.eps.yoyChange || 0) >= 0 ? "+" : ""}{stock.eps.yoyChange?.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Additional Metrics */}
        {(stock.cashFlow || stock.borrowings) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {stock.cashFlow?.current !== undefined && (
              <div className="rounded-3xl p-6" style={surfaceStyle}>
                <h3 className="text-2xl mb-4">Cash Flow from Operations</h3>
                <p className="text-4xl font-bold mb-2">Rs. {(stock.cashFlow.current / 100).toFixed(0)} Cr</p>
                {stock.cashFlow.yoyChange !== undefined && stock.cashFlow.yoyChange !== null && (
                  <p className="text-lg" style={{ color: stock.cashFlow.yoyChange >= 0 ? "#4ADE80" : "#F87171" }}>
                    YoY: {stock.cashFlow.yoyChange >= 0 ? "+" : ""}{stock.cashFlow.yoyChange.toFixed(2)}%
                  </p>
                )}
              </div>
            )}
            {stock.borrowings?.current !== undefined && (
              <div className="rounded-3xl p-6" style={surfaceStyle}>
                <h3 className="text-2xl mb-4">Total Borrowings</h3>
                <p className="text-4xl font-bold mb-2">Rs. {(stock.borrowings.current / 100).toFixed(0)} Cr</p>
                {stock.borrowings.yoyChange !== undefined && stock.borrowings.yoyChange !== null && (
                  <p className="text-lg" style={{ color: stock.borrowings.yoyChange >= 0 ? "#F87171" : "#4ADE80" }}>
                    YoY: {stock.borrowings.yoyChange >= 0 ? "+" : ""}{stock.borrowings.yoyChange.toFixed(2)}%
                  </p>
                )}
              </div>
            )}
          </motion.div>
        )}

      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  qoqData: Array<{ quarter: string; value: number }>;
  yoyData: Array<{ year: string; value: number }>;
  delay: number;
  color: string;
}

interface DailyPoint {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  price: number | null;
  volume: number | null;
}

function SimplePriceChart({ data }: { data: DailyPoint[] }) {
  const width = 1100;
  const height = 320;
  const padLeft = 44;
  const padRight = 16;
  const padTop = 16;
  const padBottom = 28;

  const values = data.flatMap((d) => [d.open, d.high, d.low, d.price]).filter((v): v is number => typeof v === "number");
  if (values.length === 0) return null;

  let min = Math.min(...values);
  let max = Math.max(...values);
  if (max === min) {
    max += 1;
    min -= 1;
  }

  const xStep = (width - padLeft - padRight) / Math.max(1, data.length - 1);
  const y = (v: number) => padTop + ((max - v) / (max - min)) * (height - padTop - padBottom);

  const toPath = (key: "open" | "high" | "low" | "price") => {
    let path = "";
    data.forEach((d, i) => {
      const val = d[key];
      if (val === null) return;
      const cmd = path ? "L" : "M";
      path += `${cmd}${padLeft + i * xStep},${y(val)} `;
    });
    return path.trim();
  };

  const openPath = toPath("open");
  const highPath = toPath("high");
  const lowPath = toPath("low");
  const closePath = toPath("price");

  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: "block" }}>
        <rect x={0} y={0} width={width} height={height} fill="transparent" />
        <line x1={padLeft} y1={padTop} x2={padLeft} y2={height - padBottom} stroke="#6A727A" strokeWidth={1} opacity={0.5} />
        <line x1={padLeft} y1={height - padBottom} x2={width - padRight} y2={height - padBottom} stroke="#6A727A" strokeWidth={1} opacity={0.5} />
        {openPath && <path d={openPath} fill="none" stroke="#F59E0B" strokeWidth={1.4} />}
        {highPath && <path d={highPath} fill="none" stroke="#4ADE80" strokeWidth={1.5} />}
        {lowPath && <path d={lowPath} fill="none" stroke="#F87171" strokeWidth={1.5} />}
        {closePath && <path d={closePath} fill="none" stroke="#3E8EDE" strokeWidth={2.6} />}
      </svg>
    </div>
  );
}

function SimpleVolumeChart({ data }: { data: DailyPoint[] }) {
  const width = 1100;
  const height = 180;
  const padLeft = 44;
  const padRight = 16;
  const padTop = 10;
  const padBottom = 22;

  const maxVol = Math.max(...data.map((d) => d.volume ?? 0), 1);
  const chartWidth = width - padLeft - padRight;
  const barWidth = Math.max(1, chartWidth / Math.max(1, data.length));

  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: "block" }}>
        <rect x={0} y={0} width={width} height={height} fill="transparent" />
        <line x1={padLeft} y1={height - padBottom} x2={width - padRight} y2={height - padBottom} stroke="#6A727A" strokeWidth={1} opacity={0.5} />
        {data.map((d, i) => {
          const vol = d.volume ?? 0;
          const barH = (vol / maxVol) * (height - padTop - padBottom);
          const x = padLeft + i * barWidth;
          const y = height - padBottom - barH;
          return <rect key={`${d.date}-${i}`} x={x} y={y} width={Math.max(1, barWidth - 0.7)} height={barH} fill="#7C9BC1" opacity={0.9} />;
        })}
      </svg>
    </div>
  );
}

function MetricCard({ title, qoqData, yoyData, delay, color }: MetricCardProps) {
  const [activeTab, setActiveTab] = useState<"qoq" | "yoy">("qoq");

  const currentData = activeTab === "qoq" ? qoqData : yoyData;
  const dataKey = activeTab === "qoq" ? "quarter" : "year";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="rounded-3xl p-6"
      style={{
        background: "linear-gradient(180deg, rgba(95,104,115,0.92) 0%, rgba(79,87,98,0.92) 100%)",
        border: "1px solid rgba(255,255,255,0.08)",
        boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
      }}
    >
      <h3 className="text-2xl mb-6">{title}</h3>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab("qoq")}
          className="px-6 py-2 rounded-lg transition-all"
          style={{
            backgroundColor: activeTab === "qoq" ? color : "#2A2E32",
            color: "#FFFFFF",
          }}
        >
          QoQ
        </button>
        <button
          onClick={() => setActiveTab("yoy")}
          className="px-6 py-2 rounded-lg transition-all"
          style={{
            backgroundColor: activeTab === "yoy" ? color : "#494F55",
            color: "#FFFFFF",
          }}
        >
          YoY
        </button>
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={currentData}>
            <defs>
              <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              contentStyle={{
                backgroundColor: "#494F55",
                border: "none",
                borderRadius: "12px",
                boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
                color: "#FFFFFF",
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={3}
              fill={`url(#gradient-${title})`}
              animationDuration={1000}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        {currentData.slice(-3).map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: delay + 0.2 + index * 0.1 }}
            className="rounded-xl p-3 text-center"
            style={{ backgroundColor: "rgba(28,32,36,0.62)", border: "1px solid rgba(255,255,255,0.08)" }}
          >
            <p className="text-xs opacity-60 mb-1" style={{ color: "#B8BCC1" }}>
              {item[dataKey as keyof typeof item]}
            </p>
            <p className="text-sm" style={{ color: color }}>
              {item.value}%
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}