# Stock Analysis Website - NSE Financial Data Platform

Complete end-to-end stock analysis platform featuring NSE data scraping, XBRL processing, MongoDB storage, and React visualization.

## Project Structure

```
ReportSquared/
├── app.py                      # Flask web scraper for NSE XBRL files
├── consolidate.py              # XBRL parser and MongoDB uploader
├── nse_scraper.py             # Original scraper script
├── .env                        # MongoDB credentials
├── xbrl_downloads/            # Downloaded XBRL files
├── Stock Analysis Website/
│   ├── src/                   # React frontend source
│   │   ├── components/        # React components
│   │   ├── services/          # API service layer
│   │   │   └── api.ts         # Backend API client
│   │   ├── styles/            # CSS styles
│   │   └── App.tsx            # Main React app
│   ├── backend/
│   │   ├── server.js          # Express API server
│   │   ├── package.json       # Backend dependencies
│   │   └── .env               # Backend MongoDB config
│   ├── .env                   # Frontend API URL config
│   └── package.json           # Frontend dependencies
```

## Features

### 1. NSE Data Scraper (Flask App)
- Web interface for downloading XBRL financial statements
- Supports all 50 Nifty stocks
- 17 quarters available (Q3 FY2021 - Q3 FY2025)
- Dual API integration:
  - 2025+ data: `integrated-filing-results` API
  - Pre-2025: `corporates-financial-results` API
- Auto-fallback: Downloads standalone if consolidated unavailable
- Filing type filters: Consolidated, Standalone, or Both

### 2. XBRL Parser & MongoDB Uploader
- Extracts quarterly financial metrics from XBRL files
- Metrics: Revenue, EBITDA, Net Profit, EPS, Cash Flow, Borrowings
- Calculates QoQ% and YoY% changes
- Handles both regular companies and banks (different XBRL tags)
- Indian Financial Year quarter labeling (Q1=Apr-Jun, Q2=Jul-Sep, etc.)
- Uploads to MongoDB Atlas

### 3. Backend REST API (Express.js)
- Connects to MongoDB Atlas
- REST endpoints:
  - `GET /api/stocks` - List all stocks
  - `GET /api/stocks/:symbol` - Get detailed stock data
  - `GET /api/stocks/search/:query` - Search by symbol/name
  - `GET /api/stocks/compare?symbols=A,B,C` - Compare stocks
  - `GET /health` - Health check
- Transforms MongoDB data to match frontend StockData interface

### 4. Frontend (React + TypeScript)
- Modern UI with Tailwind CSS
- Search functionality with autocomplete
- Individual stock pages with interactive charts (Recharts)
- Displays quarterly trends with QoQ/YoY comparisons
- Revenue, Net Profit, EBITDA visualization
- Financial metrics: Margins, EPS, Cash Flow, Borrowings

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Brave Browser (for Selenium scraping)

### 1. MongoDB Atlas Setup
1. Create a MongoDB Atlas account
2. Create a cluster (free tier works)
3. Create database user with username/password
4. Get cluster connection string
5. Update `.env` files with credentials

### 2. Backend API Setup
```bash
cd "Stock Analysis Website/backend"
npm install
# Ensure backend/.env has MongoDB credentials
node server.js
```

Backend runs on `http://localhost:5001`

### 3. Frontend Setup
```bash
cd "Stock Analysis Website"
npm install
# Ensure .env has VITE_API_URL=http://localhost:5001
npm run dev
```

Frontend runs on `http://localhost:3000` (or 3001 if 3000 is busy)

### 4. Scraper Setup (Optional - for downloading new data)
```bash
pip install flask selenium pandas lxml openpyxl pymongo python-dotenv
python app.py
```

Flask app runs on `http://localhost:5000`

## Usage

### Downloading XBRL Files
1. Navigate to `http://localhost:5000`
2. Select stocks (Ctrl+Click for multiple)
3. Choose quarter from dropdown
4. Select filing type (Consolidated/Standalone/Both)
5. Click "Download Files"
6. Files saved to `xbrl_downloads/` folder

### Processing XBRL Files
```bash
python consolidate.py
```
- Reads all XML files from `xbrl_downloads/`
- Groups by stock (requires 3 files per stock)
- Extracts quarterly metrics
- Generates Excel output: `consolidated_financials.xlsx`
- Uploads to MongoDB Atlas

### Using the Web Interface
1. Open `http://localhost:3001`
2. Search for a stock by symbol or company name
3. Click on a stock to view detailed analysis
4. View quarterly trends with interactive charts
5. Compare QoQ and YoY performance

## MongoDB Schema

### Collection: `quarterly_results`
```javascript
{
  "Stock Symbol": "RELIANCE",
  "Company Name": "RELIANCE INDUSTRIES LIMITED",
  "Revenue Q2 FY2026 (Cr)": 3870.78,
  "Revenue QoQ%": 4.12,
  "Revenue YoY%": 9.94,
  "EBITDA Q2 FY2026 (Cr)": 752.98,
  "EBITDA Margin%": 19.45,
  "Net Profit Q2 FY2026 (Cr)": 330.37,
  "Net Profit QoQ%": -28.23,
  "Net Profit YoY%": 14.33,
  "Net Profit Margin%": 8.53,
  "EPS Q2 FY2026": 13.42,
  "EPS QoQ%": -32.73,
  "EPS YoY%": -45.18,
  "Cash Flow Q2 FY2026 (Cr)": 99110,
  "Cash Flow YoY%": 7.95,
  "Borrowings Q2 FY2026 (Cr)": 348230,
  "Borrowings YoY%": 3.54
}
```

## Environment Variables

### Backend `.env` (backend/.env)
```env
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=financial_data
MONGODB_COLLECTION=quarterly_results
PORT=5001
```

### Frontend `.env` (Stock Analysis Website/.env)
```env
VITE_API_URL=http://localhost:5001
```

### Root `.env` (for consolidate.py)
```env
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=financial_data
```

## Known Issues & Limitations

1. **Missing Stocks**: HDFCLIFE and SBILIFE missing Sep 2024 quarter data (only 2 files each, need 3)
2. **Market Prices**: currentPrice/priceChange fields not populated (requires market data API integration)
3. **Bank-Specific Tags**: Some banks use different XBRL tags (handled via TAG_ALIASES)
4. **Rate Limiting**: 0.5s delay between downloads to avoid NSE rate limiting

## Technical Details

### XBRL Context Selection
- **OneD/TwoD/ThreeD**: Quarterly data (3-month period)
- **FourD**: Cumulative data (6/9-month period)
- Parser prioritizes quarterly contexts for accurate QoQ comparisons

### Indian Financial Year Quarters
- **Q1**: April - June
- **Q2**: July - September
- **Q3**: October - December
- **Q4**: January - March

### TAG_ALIASES (for XBRL parsing)
Regular companies vs Banks use different tag names:
- **Revenue**: `RevenueFromOperations` vs `Income`
- **EBITDA**: `ProfitBeforeExceptionalItemsAndTax` vs `ProfitBeforeExtraordinaryItemsAndTax`
- **Company Name**: `NameOfTheCompany` vs `NameOfBank`

## API Endpoints

### GET /api/stocks
Returns list of all stocks with symbol and name.

**Response:**
```json
[
  {
    "symbol": "RELIANCE",
    "name": "RELIANCE INDUSTRIES LIMITED"
  }
]
```

### GET /api/stocks/:symbol
Returns detailed stock data with quarterly trends.

**Response:**
```json
{
  "symbol": "RELIANCE",
  "name": "RELIANCE INDUSTRIES LIMITED",
  "currentPrice": 0,
  "priceChange": 0,
  "priceChangePercent": 0,
  "revenue": {
    "qoq": [
      {"quarter": "Q2 '26", "value": 3870.78},
      {"quarter": "Q1 '26", "value": 3717.43}
    ],
    "yoy": []
  },
  "netProfit": {
    "qoq": [...],
    "yoy": [...]
  },
  "ebitda": {
    "qoq": [...],
    "yoy": [...]
  },
  "revenueQoQ": 4.12,
  "revenueYoY": 9.94,
  "netProfitQoQ": -28.23,
  "netProfitYoY": 14.33,
  "ebitdaMargin": 19.45,
  "netProfitMargin": 8.53,
  "eps": {
    "current": 13.42,
    "qoqChange": -32.73,
    "yoyChange": -45.18
  }
}
```

### GET /api/stocks/search/:query
Search stocks by symbol or company name (case-insensitive).

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Stock Analysis API is running"
}
```

## Development

### Running in Development Mode

**Backend:**
```bash
cd "Stock Analysis Website/backend"
node server.js
```

**Frontend:**
```bash
cd "Stock Analysis Website"
npm run dev
```

**Scraper:**
```bash
python app.py
```

### Building for Production

**Frontend:**
```bash
cd "Stock Analysis Website"
npm run build
npm run preview  # Preview production build
```

## Technologies Used

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Motion (Framer)
- **Backend**: Express.js, MongoDB driver, CORS, dotenv
- **Scraper**: Flask, Selenium WebDriver, Brave Browser
- **Parser**: Python, lxml, pandas, openpyxl
- **Database**: MongoDB Atlas
- **Data Source**: NSE India (www.nseindia.com)

## License

See LICENSE file.

## Current Data Status

- **Total Stocks**: 47 (out of 50 Nifty stocks)
- **Missing**: HDFCLIFE, SBILIFE (need Sep 2024 data)
- **Quarters Available**: 3 per stock (Q2 FY2026, Q1 FY2026, Q2 FY2025)
- **Data Coverage**: July 2024 - December 2024
- **Successfully Uploaded to MongoDB**: ✓

## Next Steps

1. **Market Data Integration**: Integrate real-time price data (Alpha Vantage, Yahoo Finance)
2. **Complete Dataset**: Download missing quarters for HDFCLIFE and SBILIFE
3. **Historical Data**: Download more historical quarters (17 quarters available)
4. **Stock Comparison**: Implement multi-stock comparison feature
5. **Advanced Analytics**: Add financial ratios, peer comparisons, sector analysis
6. **Authentication**: Add user accounts for saved watchlists
7. **Alerts**: Set up alerts for significant QoQ/YoY changes
8. **Export**: Add CSV/PDF export functionality

## Support

For issues or questions, check the console logs:
- Backend: Terminal running `node server.js`
- Frontend: Browser console (F12)
- MongoDB: MongoDB Atlas dashboard
