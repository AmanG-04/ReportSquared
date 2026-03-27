const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Cache for stock prices (to avoid rate limiting)
const priceCache = new Map();
const CACHE_DURATION = 900000; // 15 minutes

// Function to fetch live price from Yahoo Finance
async function getStockPrice(symbol) {
  // Check cache first
  const cached = priceCache.get(symbol);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  try {
    // NSE symbols need .NS suffix for Yahoo Finance
    const yahooSymbol = `${symbol}.NS`;
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${yahooSymbol}`;
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    const result = response.data.chart.result[0];
    const quote = result.meta;
    const currentPrice = quote.regularMarketPrice || 0;
    const previousClose = quote.previousClose || quote.chartPreviousClose || 0;
    const priceChange = currentPrice - previousClose;
    const priceChangePercent = previousClose ? (priceChange / previousClose) * 100 : 0;

    const priceData = {
      currentPrice: parseFloat(currentPrice.toFixed(2)),
      priceChange: parseFloat(priceChange.toFixed(2)),
      priceChangePercent: parseFloat(priceChangePercent.toFixed(2))
    };

    // Cache the result
    priceCache.set(symbol, { data: priceData, timestamp: Date.now() });

    return priceData;
  } catch (error) {
    console.error(`Error fetching price for ${symbol}:`, error.message);
    // Return zeros if API fails
    return {
      currentPrice: 0,
      priceChange: 0,
      priceChangePercent: 0
    };
  }
}

// MongoDB Configuration
const MONGODB_USERNAME = process.env.MONGODB_USERNAME;
const MONGODB_PASSWORD = process.env.MONGODB_PASSWORD
  ? encodeURIComponent(process.env.MONGODB_PASSWORD)
  : '';
const MONGODB_CLUSTER = process.env.MONGODB_CLUSTER;
const MONGODB_DATABASE = process.env.MONGODB_DATABASE || 'financial_data';
const MONGODB_COLLECTION = process.env.MONGODB_COLLECTION || 'quarterly_results';
const MONGODB_URI_ENV = process.env.MONGODB_URI;
const MONGODB_ATLAS_URI = process.env.MONGODB_ATLAS_URI;
const MONGODB_LOCAL_URI = process.env.MONGODB_LOCAL_URI || 'mongodb://localhost:27017';

function buildAtlasUri() {
  if (MONGODB_ATLAS_URI) {
    return MONGODB_ATLAS_URI;
  }

  if (MONGODB_URI_ENV && MONGODB_URI_ENV.startsWith('mongodb+srv://')) {
    return MONGODB_URI_ENV;
  }

  if (!MONGODB_CLUSTER) {
    return null;
  }

  const isMongoScheme = MONGODB_CLUSTER.startsWith('mongodb://') || MONGODB_CLUSTER.startsWith('mongodb+srv://');
  if (isMongoScheme) {
    return MONGODB_CLUSTER.startsWith('mongodb+srv://') ? MONGODB_CLUSTER : null;
  }

  const isLocalHost = /^(localhost|127\.0\.0\.1)(:\d+)?$/i.test(MONGODB_CLUSTER);
  if (isLocalHost) {
    return null;
  }

  if (!MONGODB_USERNAME || !MONGODB_PASSWORD) {
    return null;
  }

  return `mongodb+srv://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@${MONGODB_CLUSTER}/?appName=Cluster0`;
}

function buildLocalUri() {
  if (MONGODB_LOCAL_URI) {
    return MONGODB_LOCAL_URI;
  }

  if (MONGODB_URI_ENV && MONGODB_URI_ENV.startsWith('mongodb://')) {
    return MONGODB_URI_ENV;
  }

  return 'mongodb://localhost:27017';
}

let db;
let collection;

// Connect to MongoDB
async function connectToMongoDB() {
  const atlasUri = buildAtlasUri();
  const localUri = buildLocalUri();
  const connectionCandidates = [];

  if (atlasUri) {
    connectionCandidates.push({ label: 'Atlas', uri: atlasUri });
  }
  if (localUri) {
    connectionCandidates.push({ label: 'Local', uri: localUri });
  }

  if (connectionCandidates.length === 0) {
    console.error('✗ Failed to connect to MongoDB: no valid URI configured');
    process.exit(1);
  }

  let lastError;

  for (const candidate of connectionCandidates) {
    try {
      const client = new MongoClient(candidate.uri, { serverSelectionTimeoutMS: 5000 });
      await client.connect();
      db = client.db(MONGODB_DATABASE);
      collection = db.collection(MONGODB_COLLECTION);
      console.log(`✓ Connected to MongoDB (${candidate.label})`);
      console.log(`✓ Using database: ${MONGODB_DATABASE}, collection: ${MONGODB_COLLECTION}`);

      if (candidate.label === 'Local' && atlasUri) {
        console.log('ℹ Atlas unavailable, using local MongoDB fallback');
      }

      return;
    } catch (error) {
      lastError = error;
      console.warn(`⚠ MongoDB ${candidate.label} connection failed: ${error.message}`);
    }
  }

  console.error('✗ Failed to connect to MongoDB with all configured targets:', lastError);
  process.exit(1);
}

// Helper function to transform MongoDB data to frontend format
function transformStockData(doc) {
  if (!doc) return null;

  // Extract quarter labels from column names
  const getQuarterLabel = (colName) => {
    const match = colName.match(/Q(\d) FY(\d{4})/);
    if (match) {
      return `Q${match[1]} '${match[2].slice(2)}`;
    }
    return colName;
  };

  // Extract absolute values and calculate percentage changes
  const extractMetricData = (metricName) => {
    const values = [];
    
    // Get all columns for this metric (Q2 FY2026, Q1 FY2026, Q2 FY2025)
    Object.keys(doc).forEach(key => {
      if (key.includes(metricName) && key.includes('FY') && key.includes('(Cr)')) {
        const match = key.match(new RegExp(`${metricName} (Q\\d FY\\d{4})`));
        if (match) {
          const quarter = getQuarterLabel(match[1]);
          const value = doc[key];
          if (value !== null && value !== undefined) {
            values.push({ quarter, value: parseFloat(value) });
          }
        }
      }
    });

    // Sort by year and quarter (newest first)
    values.sort((a, b) => {
      const yearA = parseInt(a.quarter.match(/'(\d+)/)[1]);
      const yearB = parseInt(b.quarter.match(/'(\d+)/)[1]);
      const qA = parseInt(a.quarter.match(/Q(\d)/)[1]);
      const qB = parseInt(b.quarter.match(/Q(\d)/)[1]);
      if (yearA !== yearB) return yearB - yearA;
      return qB - qA;
    });

    // Calculate QoQ percentage changes
    const qoqData = [];
    for (let i = 0; i < values.length; i++) {
      if (i < values.length - 1) {
        const pctChange = ((values[i].value - values[i + 1].value) / values[i + 1].value) * 100;
        qoqData.push({
          quarter: values[i].quarter,
          value: parseFloat(pctChange.toFixed(2))
        });
      }
    }

    // Calculate YoY percentage changes (compare same quarters across years)
    const yoyData = [];
    const quarterGroups = {};
    
    values.forEach(item => {
      const quarterMatch = item.quarter.match(/Q(\d)/);
      const yearMatch = item.quarter.match(/'(\d+)/);
      if (quarterMatch && yearMatch) {
        const qNum = quarterMatch[1];
        if (!quarterGroups[qNum]) {
          quarterGroups[qNum] = [];
        }
        quarterGroups[qNum].push(item);
      }
    });

    Object.keys(quarterGroups).forEach(qNum => {
      const quarters = quarterGroups[qNum].sort((a, b) => {
        const yearA = parseInt(a.quarter.match(/'(\d+)/)[1]);
        const yearB = parseInt(b.quarter.match(/'(\d+)/)[1]);
        return yearB - yearA;
      });

      if (quarters.length >= 2) {
        for (let i = 0; i < quarters.length - 1; i++) {
          const pctChange = ((quarters[i].value - quarters[i + 1].value) / quarters[i + 1].value) * 100;
          const yearA = quarters[i].quarter.match(/'(\d+)/)[1];
          const yearB = quarters[i + 1].quarter.match(/'(\d+)/)[1];
          yoyData.push({
            year: `FY'${yearA} vs FY'${yearB}`,
            value: parseFloat(pctChange.toFixed(2))
          });
        }
      }
    });

    return { qoq: qoqData, yoy: yoyData };
  };

  const revenueData = extractMetricData('Revenue');
  const netProfitData = extractMetricData('Net Profit');
  const ebitdaData = extractMetricData('EBITDA');

  return {
    symbol: doc.StockSymbol || 'UNKNOWN',
    name: doc.CompanyName || 'Unknown Company',
    // Price data will be added dynamically
    currentPrice: 0,
    priceChange: 0,
    priceChangePercent: 0,
    revenue: revenueData,
    netProfit: netProfitData,
    ebitda: ebitdaData,
    // Additional data from MongoDB
    revenueQoQ: doc['Revenue QoQ%'],
    revenueYoY: doc['Revenue YoY%'],
    netProfitQoQ: doc['Net Profit QoQ%'],
    netProfitYoY: doc['Net Profit YoY%'],
    ebitdaMargin: doc['EBITDA Margin (%)'],
    netProfitMargin: doc['Net Profit Margin (%)'],
    eps: {
      current: doc[Object.keys(doc).find(k => k.includes('Basic EPS Q') && k.includes('FY2026'))],
      qoqChange: doc['Basic EPS QoQ%'],
      yoyChange: doc['Basic EPS YoY%']
    },
    cashFlow: {
      current: doc[Object.keys(doc).find(k => k.includes('Cash Flow from Ops Q') && k.includes('FY2026'))],
      qoqChange: doc['Cash Flow from Ops QoQ%'],
      yoyChange: doc['Cash Flow from Ops YoY%']
    },
    borrowings: {
      current: doc[Object.keys(doc).find(k => k.includes('Borrowings Q') && k.includes('FY2026'))],
      qoqChange: doc['Borrowings QoQ%'],
      yoyChange: doc['Borrowings YoY%']
    }
  };
}

// API Routes

// Get all stock symbols
app.get('/api/stocks', async (req, res) => {
  try {
    const stocks = await collection.find({}, { projection: { StockSymbol: 1, CompanyName: 1, _id: 0 } }).toArray();
    const stockList = stocks.map(s => ({
      symbol: s.StockSymbol,
      name: s.CompanyName
    }));
    res.json(stockList);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).json({ error: 'Failed to fetch stocks' });
  }
});

// Get stock data by symbol
app.get('/api/stocks/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const doc = await collection.findOne({ StockSymbol: symbol.toUpperCase() });
    
    if (!doc) {
      return res.status(404).json({ error: 'Stock not found' });
    }

    const stockData = transformStockData(doc);
    
    // Fetch live price data
    const priceData = await getStockPrice(symbol.toUpperCase());
    stockData.currentPrice = priceData.currentPrice;
    stockData.priceChange = priceData.priceChange;
    stockData.priceChangePercent = priceData.priceChangePercent;
    
    res.json(stockData);
  } catch (error) {
    console.error('Error fetching stock:', error);
    res.status(500).json({ error: 'Failed to fetch stock data' });
  }
});

// Search stocks
app.get('/api/stocks/search/:query', async (req, res) => {
  try {
    const { query } = req.params;
    const stocks = await collection.find({
      $or: [
        { StockSymbol: { $regex: query, $options: 'i' } },
        { CompanyName: { $regex: query, $options: 'i' } }
      ]
    }, { projection: { StockSymbol: 1, CompanyName: 1, _id: 0 } }).limit(10).toArray();
    
    const stockList = stocks.map(s => ({
      symbol: s.StockSymbol,
      name: s.CompanyName
    }));
    res.json(stockList);
  } catch (error) {
    console.error('Error searching stocks:', error);
    res.status(500).json({ error: 'Failed to search stocks' });
  }
});

// Get all stock data (for comparison)
app.get('/api/stocks/compare', async (req, res) => {
  try {
    const { symbols } = req.query;
    const symbolArray = symbols.split(',').map(s => s.trim().toUpperCase());
    
    const docs = await collection.find({ StockSymbol: { $in: symbolArray } }).toArray();
    const stocksData = docs.map(doc => transformStockData(doc));
    
    res.json(stocksData);
  } catch (error) {
    console.error('Error comparing stocks:', error);
    res.status(500).json({ error: 'Failed to compare stocks' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Stock Analysis API is running' });
});

// Start server
connectToMongoDB().then(() => {
  app.listen(PORT, () => {
    console.log(`\n🚀 Server running on http://localhost:${PORT}`);
    console.log(`📊 API endpoints:`);
    console.log(`   GET /api/stocks - Get all stocks`);
    console.log(`   GET /api/stocks/:symbol - Get specific stock data`);
    console.log(`   GET /api/stocks/search/:query - Search stocks`);
    console.log(`   GET /health - Health check\n`);
  });
});
