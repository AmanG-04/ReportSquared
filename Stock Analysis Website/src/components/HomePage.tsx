import { useState, useEffect } from "react";
import { Search, TrendingUp } from "lucide-react";
import { motion } from "motion/react";
import { stockAPI, type StockSymbol } from "../services/api";

interface HomePageProps {
  onSelectStock: (symbol: string) => void;
}

export function HomePage({ onSelectStock }: HomePageProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredStocks, setFilteredStocks] = useState<StockSymbol[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [allStocks, setAllStocks] = useState<StockSymbol[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    stockAPI.getAllStocks()
      .then(stocks => {
        setAllStocks(stocks);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load stocks:', err);
        setError('Failed to load stocks. Please check if the backend server is running.');
        setLoading(false);
      });
  }, []);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim() && allStocks.length > 0) {
      const filtered = allStocks.filter((stock) =>
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredStocks(filtered);
      setShowSuggestions(true);
    } else {
      setFilteredStocks([]);
      setShowSuggestions(false);
    }
  };

  const handleSelectStock = (symbol: string) => {
    setSearchQuery("");
    setShowSuggestions(false);
    onSelectStock(symbol);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <div className="text-white text-xl">Loading stocks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <div className="text-red-400 text-xl mb-4">{error}</div>
        <div className="text-white opacity-60 text-center max-w-md">
          Make sure the backend server is running on port 5001:
          <div className="mt-2 p-4 bg-black/30 rounded-lg text-sm font-mono text-left">
            cd backend<br/>
            npm install<br/>
            node server.js
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-4xl w-full"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-6">
            <TrendingUp className="w-12 h-12" style={{ color: "#3E8EDE" }} />
            <h1 className="text-6xl">EquityLens</h1>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="relative mb-12"
        >
          <div className="relative">
            {/* Subtle glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#3E8EDE] to-[#5BA4F0] opacity-10 blur-2xl rounded-2xl"></div>
            
            <div
              className="relative flex items-center gap-4 px-8 py-5 rounded-2xl backdrop-blur-md border transition-all duration-300 hover:border-opacity-40"
              style={{
                backgroundColor: "rgba(0, 0, 0, 0.5)",
                borderColor: "rgba(62, 142, 222, 0.3)",
                borderWidth: "1px",
                boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)",
              }}
            >
              <Search className="w-6 h-6 opacity-50" style={{ color: "#3E8EDE" }} />
              <input
                type="text"
                placeholder="Search for a stock..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="flex-1 bg-transparent outline-none text-lg placeholder-opacity-40"
                style={{ color: "#FFFFFF" }}
              />
            </div>
          </div>

          {showSuggestions && filteredStocks.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute top-full mt-3 w-full rounded-2xl overflow-hidden backdrop-blur-md border"
              style={{
                backgroundColor: "rgba(58, 63, 69, 0.95)",
                borderColor: "rgba(62, 142, 222, 0.2)",
                boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
              }}
            >
              {filteredStocks.map((stock, index) => (
                <motion.button
                  key={stock.symbol}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.03 }}
                  onClick={() => handleSelectStock(stock.symbol)}
                  className="w-full px-8 py-4 text-left transition-all duration-200 relative group"
                  style={{
                    backgroundColor: "transparent",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "rgba(62, 142, 222, 0.1)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "transparent";
                  }}
                >
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold">{stock.symbol}</span>
                    <span className="text-sm opacity-60">{stock.name}</span>
                  </div>
                  <div
                    className="absolute bottom-0 left-8 right-8 h-px opacity-10"
                    style={{ backgroundColor: "#3E8EDE" }}
                  />
                </motion.button>
              ))}
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
}