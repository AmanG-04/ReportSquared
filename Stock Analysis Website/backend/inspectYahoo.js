const axios = require('axios');

const inputSymbol = process.argv[2] || 'TCS';
const yahooSymbol = inputSymbol.toUpperCase().endsWith('.NS') ? inputSymbol.toUpperCase() : `${inputSymbol.toUpperCase()}.NS`;
const url = `https://query1.finance.yahoo.com/v8/finance/chart/${yahooSymbol}?range=6mo&interval=1d`;

async function main() {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    console.log(`Fetched Yahoo Finance /v8/finance/chart payload for ${yahooSymbol}:`);
    console.dir(response.data, { depth: null, maxArrayLength: null });
  } catch (error) {
    if (error.response) {
      console.error('Yahoo Finance API responded with an error:', error.response.status, error.response.statusText);
      console.error(error.response.data);
    } else {
      console.error('Failed to fetch data:', error.message);
    }
    process.exit(1);
  }
}

main();
