const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

export interface StockData {
  symbol: string;
  name: string;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  revenue: {
    qoq: Array<{ quarter: string; value: number }>;
    yoy: Array<{ year: string; value: number }>;
  };
  netProfit: {
    qoq: Array<{ quarter: string; value: number }>;
    yoy: Array<{ year: string; value: number }>;
  };
  ebitda: {
    qoq: Array<{ quarter: string; value: number }>;
    yoy: Array<{ year: string; value: number }>;
  };
  // Additional fields from MongoDB
  revenueQoQ?: number;
  revenueYoY?: number;
  netProfitQoQ?: number;
  netProfitYoY?: number;
  ebitdaMargin?: number;
  netProfitMargin?: number;
  eps?: {
    current: number;
    qoqChange: number;
    yoyChange: number;
  };
  cashFlow?: {
    current: number;
    qoqChange: number;
    yoyChange: number;
  };
  borrowings?: {
    current: number;
    qoqChange: number;
    yoyChange: number;
  };
}

export interface StockSymbol {
  symbol: string;
  name: string;
}

class StockAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async getAllStocks(): Promise<StockSymbol[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/stocks`);
      if (!response.ok) {
        throw new Error('Failed to fetch stocks');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching stocks:', error);
      throw error;
    }
  }

  async getStockData(symbol: string): Promise<StockData> {
    try {
      const response = await fetch(`${this.baseURL}/api/stocks/${symbol}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch stock data for ${symbol}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching stock ${symbol}:`, error);
      throw error;
    }
  }

  async searchStocks(query: string): Promise<StockSymbol[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/stocks/search/${query}`);
      if (!response.ok) {
        throw new Error('Failed to search stocks');
      }
      return await response.json();
    } catch (error) {
      console.error('Error searching stocks:', error);
      throw error;
    }
  }

  async compareStocks(symbols: string[]): Promise<StockData[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/stocks/compare?symbols=${symbols.join(',')}`);
      if (!response.ok) {
        throw new Error('Failed to compare stocks');
      }
      return await response.json();
    } catch (error) {
      console.error('Error comparing stocks:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

export const stockAPI = new StockAPI();
