# NSE XBRL Downloader - Web Frontend

A simple web interface to download consolidated financial filings (XBRL) from NSE for Nifty 50 companies.

## Features

✅ **Easy Stock Selection** - Pick from all 50 Nifty companies
✅ **Date Picker** - Simply select the quarter-end date
✅ **Consolidated Files** - Automatically downloads consolidated filings
✅ **File Management** - View and download all files from the interface
✅ **Real-time Progress** - See download progress in real-time

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and go to:
```
http://localhost:5000
```

## Usage

1. **Select Date**: Choose the quarter-end date (e.g., 30-Jun, 30-Sep, 31-Dec, 31-Mar)
2. **Select Stocks**: Check the boxes for companies you want to download
3. **Click Download**: Hit the download button
4. **Wait**: Monitor the download progress
5. **Download Files**: Click on any file to download it

## How it Works

- The app connects to NSE's API to fetch integrated filing data
- It automatically downloads consolidated versions of the filings
- Files are saved in the `xbrl_downloads` folder
- You can manage and download files directly from the web interface

## Files Structure

```
ReportSquared/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
└── xbrl_downloads/       # Downloaded files (auto-created)
```

## Notes

- Make sure you have an active internet connection
- NSE API may have rate limits, so downloads might be slightly delayed
- Files are named as: `{SYMBOL}_{DATE}_{TYPE}.xml`
  - Example: `RELIANCE_30-JUN-2025_Consolidated.xml`

## Troubleshooting

**Port 5000 already in use?**
```bash
python app.py --port 5001
```

**Files not downloading?**
- Check your internet connection
- Verify the stock symbol and date are correct
- Check that NSE website is accessible

## License

MIT
