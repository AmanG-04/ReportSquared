const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { MongoClient } = require('mongodb');
const dotenv = require('dotenv');

// Load environment variables (try repo root first, then project-level .env files)
const envCandidates = [
  path.resolve(__dirname, '../../../.env'),
  path.resolve(__dirname, '../../.env'),
  path.resolve(__dirname, '../.env')
];

let envLoaded = false;
for (const envPath of envCandidates) {
  if (fs.existsSync(envPath)) {
    dotenv.config({ path: envPath });
    envLoaded = true;
    break;
  }
}

if (!envLoaded) {
  dotenv.config();
}

const MONGODB_URI = process.env.MONGODB_URI_LOCAL || process.env.MONGODB_URI;

if (!MONGODB_URI) {
  console.error('Missing MONGODB_URI_LOCAL or MONGODB_URI in environment variables.');
  process.exit(1);
}

const DATA_FILE = path.resolve(__dirname, '../nifty100.json');
const PRICE_COLLECTION = 'daily_prices';
const RANGE = '1y';
const INTERVAL = '1d';
const REQUEST_SLEEP_MS = 750;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function loadSymbols() {
  if (!fs.existsSync(DATA_FILE)) {
    console.error(`Symbol list not found at ${DATA_FILE}`);
    process.exit(1);
  }
  const raw = fs.readFileSync(DATA_FILE, 'utf8');
  return JSON.parse(raw).map((entry) => entry.symbol);
}

async function fetchYahooData(symbol) {
  const yahooSymbol = symbol.endsWith('.NS') ? symbol : `${symbol}.NS`;
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${yahooSymbol}`;
  const params = { range: RANGE, interval: INTERVAL };

  const response = await axios.get(url, {
    params,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      Accept: 'application/json,text/javascript,*/*;q=0.01',
      Referer: 'https://finance.yahoo.com/'
    }
  });

  const chart = response.data?.chart;
  if (!chart || chart.error || !Array.isArray(chart.result) || !chart.result[0]) {
    throw new Error(chart?.error?.description || 'Unexpected Yahoo response');
  }

  const result = chart.result[0];
  const timestamps = result.timestamp || [];
  const quotes = result.indicators?.quote?.[0];
  const adjCloseArr = result.indicators?.adjclose?.[0]?.adjclose || [];

  if (!quotes) {
    throw new Error('Missing quote data from Yahoo response');
  }

  const { open = [], high = [], low = [], close = [], volume = [] } = quotes;

  return timestamps.reduce((acc, ts, idx) => {
    const dataPoint = {
      symbol,
      timestamp: ts,
      open: open[idx] ?? null,
      high: high[idx] ?? null,
      low: low[idx] ?? null,
      close: close[idx] ?? null,
      adjClose: adjCloseArr[idx] ?? null,
      volume: volume[idx] ?? null
    };

    const hasNullValue = Object.values(dataPoint).some((value) => value === null);
    if (!hasNullValue) {
      acc.push(dataPoint);
    }
    return acc;
  }, []);
}

async function upsertPrices(collection, documents) {
  if (!documents.length) return;

  const operations = documents.map((doc) => ({
    updateOne: {
      filter: { symbol: doc.symbol, timestamp: doc.timestamp },
      update: { $set: doc },
      upsert: true
    }
  }));

  await collection.bulkWrite(operations, { ordered: false });
}

async function main() {
  const symbols = loadSymbols();
  console.log(`Seeding price history for ${symbols.length} symbols into ${MONGODB_URI}`);

  const client = new MongoClient(MONGODB_URI);
  await client.connect();
  const db = client.db();
  const collection = db.collection(PRICE_COLLECTION);

  let success = 0;
  for (const symbol of symbols) {
    try {
      console.log(`Fetching ${symbol} (${RANGE}/${INTERVAL})...`);
      const docs = await fetchYahooData(symbol);
      await upsertPrices(collection, docs);
      success += 1;
      console.log(`✓ ${symbol}: stored ${docs.length} records`);
    } catch (error) {
      console.error(`✗ ${symbol}: ${error.message}`);
    }
    await sleep(REQUEST_SLEEP_MS);
  }

  console.log(`Completed. Successful symbols: ${success}/${symbols.length}`);
  await client.close();
}

main().catch((error) => {
  console.error('Fatal error seeding price data:', error);
  process.exit(1);
});
