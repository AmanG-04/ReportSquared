import { useState, useEffect } from "react";
import { HomePage } from "./components/HomePage";
import { StockPage } from "./components/StockPage";
import { DynamicBackground } from "./components/DynamicBackground";
import { DottedSurface } from "./components/ui/dotted-surface";
import { stockAPI, type StockData } from "./services/api";
import "./styles/globals.css";

export default function App() {
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedStock) {
      setLoading(true);
      setError(null);
      stockAPI.getStockData(selectedStock)
        .then(data => {
          setStockData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load stock data:', err);
          setError('Failed to load stock data. Please try again.');
          setLoading(false);
        });
    } else {
      setStockData(null);
    }
  }, [selectedStock]);

  const handleSelectStock = (symbol: string) => {
    setSelectedStock(symbol);
  };

  const handleBack = () => {
    setSelectedStock(null);
    setStockData(null);
    setError(null);
  };

  return (
    <div className="min-h-screen relative" style={{ backgroundColor: "#000000" }}>
      <DynamicBackground />
      <DottedSurface className="opacity-30" />
      <div className="relative z-10">
        {!selectedStock ? (
          <HomePage onSelectStock={handleSelectStock} />
        ) : loading ? (
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-white text-xl">Loading stock data...</div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center min-h-screen">
            <div className="text-red-400 text-xl mb-4">{error}</div>
            <button 
              onClick={handleBack}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go Back
            </button>
          </div>
        ) : stockData ? (
          <StockPage stock={stockData} onBack={handleBack} />
        ) : null}
      </div>
    </div>
  );
}