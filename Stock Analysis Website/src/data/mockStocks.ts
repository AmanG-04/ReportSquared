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
  cashFlow?: {
    current: number;
    yoyChange?: number | null;
  };
  ebitdaMargin?: number;
  netProfitMargin?: number;
  eps?: {
    current: number;
    yoyChange?: number | null;
  };
  borrowings?: {
    current: number;
    yoyChange?: number | null;
  };
}

export const stocksData: Record<string, StockData> = {
  AAPL: {
    symbol: "AAPL",
    name: "Apple Inc.",
    currentPrice: 189.95,
    priceChange: 2.45,
    priceChangePercent: 1.31,
    revenue: {
      qoq: [
        { quarter: "Q1 '23", value: 117.2 },
        { quarter: "Q2 '23", value: 94.8 },
        { quarter: "Q3 '23", value: 81.8 },
        { quarter: "Q4 '23", value: 89.5 },
        { quarter: "Q1 '24", value: 119.6 },
        { quarter: "Q2 '24", value: 90.8 },
      ],
      yoy: [
        { year: "2019", value: 260.2 },
        { year: "2020", value: 274.5 },
        { year: "2021", value: 365.8 },
        { year: "2022", value: 394.3 },
        { year: "2023", value: 383.3 },
      ],
    },
    netProfit: {
      qoq: [
        { quarter: "Q1 '23", value: 30.0 },
        { quarter: "Q2 '23", value: 24.2 },
        { quarter: "Q3 '23", value: 21.4 },
        { quarter: "Q4 '23", value: 23.0 },
        { quarter: "Q1 '24", value: 33.9 },
        { quarter: "Q2 '24", value: 23.6 },
      ],
      yoy: [
        { year: "2019", value: 55.3 },
        { year: "2020", value: 57.4 },
        { year: "2021", value: 94.7 },
        { year: "2022", value: 99.8 },
        { year: "2023", value: 97.0 },
      ],
    },
    ebitda: {
      qoq: [
        { quarter: "Q1 '23", value: 41.2 },
        { quarter: "Q2 '23", value: 33.5 },
        { quarter: "Q3 '23", value: 29.8 },
        { quarter: "Q4 '23", value: 32.1 },
        { quarter: "Q1 '24", value: 44.5 },
        { quarter: "Q2 '24", value: 32.9 },
      ],
      yoy: [
        { year: "2019", value: 76.5 },
        { year: "2020", value: 77.3 },
        { year: "2021", value: 120.2 },
        { year: "2022", value: 130.5 },
        { year: "2023", value: 125.8 },
      ],
    },
  },
  MSFT: {
    symbol: "MSFT",
    name: "Microsoft Corporation",
    currentPrice: 374.27,
    priceChange: -3.12,
    priceChangePercent: -0.83,
    revenue: {
      qoq: [
        { quarter: "Q1 '23", value: 52.9 },
        { quarter: "Q2 '23", value: 56.2 },
        { quarter: "Q3 '23", value: 61.9 },
        { quarter: "Q4 '23", value: 56.5 },
        { quarter: "Q1 '24", value: 56.5 },
        { quarter: "Q2 '24", value: 62.0 },
      ],
      yoy: [
        { year: "2019", value: 125.8 },
        { year: "2020", value: 143.0 },
        { year: "2021", value: 168.1 },
        { year: "2022", value: 198.3 },
        { year: "2023", value: 211.9 },
      ],
    },
    netProfit: {
      qoq: [
        { quarter: "Q1 '23", value: 16.7 },
        { quarter: "Q2 '23", value: 18.3 },
        { quarter: "Q3 '23", value: 20.1 },
        { quarter: "Q4 '23", value: 18.3 },
        { quarter: "Q1 '24", value: 18.3 },
        { quarter: "Q2 '24", value: 21.9 },
      ],
      yoy: [
        { year: "2019", value: 39.2 },
        { year: "2020", value: 44.3 },
        { year: "2021", value: 61.3 },
        { year: "2022", value: 72.7 },
        { year: "2023", value: 72.4 },
      ],
    },
    ebitda: {
      qoq: [
        { quarter: "Q1 '23", value: 24.8 },
        { quarter: "Q2 '23", value: 27.1 },
        { quarter: "Q3 '23", value: 30.2 },
        { quarter: "Q4 '23", value: 27.5 },
        { quarter: "Q1 '24", value: 28.1 },
        { quarter: "Q2 '24", value: 32.4 },
      ],
      yoy: [
        { year: "2019", value: 58.3 },
        { year: "2020", value: 65.1 },
        { year: "2021", value: 85.7 },
        { year: "2022", value: 100.5 },
        { year: "2023", value: 107.2 },
      ],
    },
  },
  GOOGL: {
    symbol: "GOOGL",
    name: "Alphabet Inc.",
    currentPrice: 139.84,
    priceChange: 1.78,
    priceChangePercent: 1.29,
    revenue: {
      qoq: [
        { quarter: "Q1 '23", value: 69.8 },
        { quarter: "Q2 '23", value: 74.6 },
        { quarter: "Q3 '23", value: 76.7 },
        { quarter: "Q4 '23", value: 86.3 },
        { quarter: "Q1 '24", value: 80.5 },
        { quarter: "Q2 '24", value: 84.7 },
      ],
      yoy: [
        { year: "2019", value: 161.9 },
        { year: "2020", value: 182.5 },
        { year: "2021", value: 257.6 },
        { year: "2022", value: 282.8 },
        { year: "2023", value: 307.4 },
      ],
    },
    netProfit: {
      qoq: [
        { quarter: "Q1 '23", value: 15.1 },
        { quarter: "Q2 '23", value: 18.4 },
        { quarter: "Q3 '23", value: 19.7 },
        { quarter: "Q4 '23", value: 20.7 },
        { quarter: "Q1 '24", value: 23.7 },
        { quarter: "Q2 '24", value: 23.6 },
      ],
      yoy: [
        { year: "2019", value: 34.3 },
        { year: "2020", value: 40.3 },
        { year: "2021", value: 76.0 },
        { year: "2022", value: 59.9 },
        { year: "2023", value: 73.8 },
      ],
    },
    ebitda: {
      qoq: [
        { quarter: "Q1 '23", value: 21.5 },
        { quarter: "Q2 '23", value: 25.8 },
        { quarter: "Q3 '23", value: 27.3 },
        { quarter: "Q4 '23", value: 28.9 },
        { quarter: "Q1 '24", value: 32.4 },
        { quarter: "Q2 '24", value: 32.2 },
      ],
      yoy: [
        { year: "2019", value: 47.2 },
        { year: "2020", value: 56.1 },
        { year: "2021", value: 105.4 },
        { year: "2022", value: 92.7 },
        { year: "2023", value: 103.5 },
      ],
    },
  },
  TSLA: {
    symbol: "TSLA",
    name: "Tesla, Inc.",
    currentPrice: 242.84,
    priceChange: 5.67,
    priceChangePercent: 2.39,
    revenue: {
      qoq: [
        { quarter: "Q1 '23", value: 23.3 },
        { quarter: "Q2 '23", value: 24.9 },
        { quarter: "Q3 '23", value: 23.4 },
        { quarter: "Q4 '23", value: 25.2 },
        { quarter: "Q1 '24", value: 21.3 },
        { quarter: "Q2 '24", value: 25.5 },
      ],
      yoy: [
        { year: "2019", value: 24.6 },
        { year: "2020", value: 31.5 },
        { year: "2021", value: 53.8 },
        { year: "2022", value: 81.5 },
        { year: "2023", value: 96.8 },
      ],
    },
    netProfit: {
      qoq: [
        { quarter: "Q1 '23", value: 2.5 },
        { quarter: "Q2 '23", value: 2.7 },
        { quarter: "Q3 '23", value: 1.9 },
        { quarter: "Q4 '23", value: 2.5 },
        { quarter: "Q1 '24", value: 1.1 },
        { quarter: "Q2 '24", value: 1.5 },
      ],
      yoy: [
        { year: "2019", value: -0.9 },
        { year: "2020", value: 0.7 },
        { year: "2021", value: 5.5 },
        { year: "2022", value: 12.6 },
        { year: "2023", value: 9.6 },
      ],
    },
    ebitda: {
      qoq: [
        { quarter: "Q1 '23", value: 4.2 },
        { quarter: "Q2 '23", value: 4.5 },
        { quarter: "Q3 '23", value: 3.8 },
        { quarter: "Q4 '23", value: 4.4 },
        { quarter: "Q1 '24", value: 2.9 },
        { quarter: "Q2 '24", value: 3.6 },
      ],
      yoy: [
        { year: "2019", value: 2.1 },
        { year: "2020", value: 4.3 },
        { year: "2021", value: 9.7 },
        { year: "2022", value: 18.6 },
        { year: "2023", value: 16.9 },
      ],
    },
  },
};

export const stockSymbols = Object.keys(stocksData);
