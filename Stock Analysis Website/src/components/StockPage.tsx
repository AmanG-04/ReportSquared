import { useState } from "react";
import { motion } from "motion/react";
import { ArrowLeft, TrendingUp, TrendingDown } from "lucide-react";
import { LineChart, Line, ResponsiveContainer, Tooltip, AreaChart, Area } from "recharts";
import { StockData } from "../data/mockStocks";

interface StockPageProps {
  stock: StockData;
  onBack: () => void;
}

export function StockPage({ stock, onBack }: StockPageProps) {
  const isPositive = stock.priceChange >= 0;

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
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h1 className="text-5xl">{stock.symbol}</h1>
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

        {/* Key Metrics Summary Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
        >
          {stock.ebitdaMargin !== undefined && (
            <div className="rounded-2xl p-4" style={{ backgroundColor: "#5A6169" }}>
              <p className="text-sm opacity-60 mb-1">EBITDA Margin</p>
              <p className="text-2xl font-bold">{stock.ebitdaMargin?.toFixed(2)}%</p>
            </div>
          )}
          {stock.netProfitMargin !== undefined && (
            <div className="rounded-2xl p-4" style={{ backgroundColor: "#5A6169" }}>
              <p className="text-sm opacity-60 mb-1">Net Profit Margin</p>
              <p className="text-2xl font-bold">{stock.netProfitMargin?.toFixed(2)}%</p>
            </div>
          )}
          {stock.eps?.current !== undefined && (
            <div className="rounded-2xl p-4" style={{ backgroundColor: "#5A6169" }}>
              <p className="text-sm opacity-60 mb-1">EPS (Current)</p>
              <p className="text-2xl font-bold">Rs. {stock.eps.current?.toFixed(2)}</p>
            </div>
          )}
          {stock.cashFlow?.current !== undefined && (
            <div className="rounded-2xl p-4" style={{ backgroundColor: "#5A6169" }}>
              <p className="text-sm opacity-60 mb-1">Cash Flow (Cr)</p>
              <p className="text-2xl font-bold">{(stock.cashFlow.current / 100).toFixed(0)}</p>
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
            <div className="rounded-3xl p-6" style={{ backgroundColor: "#5A6169", boxShadow: "0 10px 40px rgba(0,0,0,0.3)" }}>
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
              <div className="rounded-3xl p-6" style={{ backgroundColor: "#5A6169", boxShadow: "0 10px 40px rgba(0,0,0,0.3)" }}>
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
              <div className="rounded-3xl p-6" style={{ backgroundColor: "#5A6169", boxShadow: "0 10px 40px rgba(0,0,0,0.3)" }}>
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
        backgroundColor: "#5A6169",
        boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
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
            style={{ backgroundColor: "#2A2E32" }}
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