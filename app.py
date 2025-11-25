from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'xbrl_downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store download progress
download_progress = {'status': 'idle', 'message': '', 'files': []}

# NSE API details
u_if = "https://www.nseindia.com/api/integrated-filing-results"  # For 2025 data
u_old = "https://www.nseindia.com/api/corporates-financial-results"  # For older data
h = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-integrated-filing"
}

# Quarters available in integrated filing API (2025 and newer)
INTEGRATED_FILING_QUARTERS = ['30-Sep-2025', '30-Jun-2025', '31-Mar-2025']

# List of Nifty 50 companies for dropdown
NIFTY50 = [
    {'symbol': 'ADANIPORTS', 'name': 'Adani Ports and Special Economic Zone Ltd.'},
    {'symbol': 'APOLLOHOSP', 'name': 'Apollo Hospitals Enterprise Ltd.'},
    {'symbol': 'ASIANPAINT', 'name': 'Asian Paints Ltd.'},
    {'symbol': 'AXISBANK', 'name': 'Axis Bank Ltd.'},
    {'symbol': 'BAJAJ-AUTO', 'name': 'Bajaj Auto Ltd.'},
    {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance Ltd.'},
    {'symbol': 'BAJAJFINSV', 'name': 'Bajaj Finserv Ltd.'},
    {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.'},
    {'symbol': 'BPCL', 'name': 'Bharat Petroleum Corporation Ltd.'},
    {'symbol': 'BRITANNIA', 'name': 'Britannia Industries Ltd.'},
    {'symbol': 'CIPLA', 'name': 'Cipla Ltd.'},
    {'symbol': 'COALINDIA', 'name': 'Coal India Ltd.'},
    {'symbol': 'DIVISLAB', 'name': 'Divi\'s Laboratories Ltd.'},
    {'symbol': 'DRREDDY', 'name': 'Dr. Reddy\'s Laboratories Ltd.'},
    {'symbol': 'EICHERMOT', 'name': 'Eicher Motors Ltd.'},
    {'symbol': 'GRASIM', 'name': 'Grasim Industries Ltd.'},
    {'symbol': 'HCLTECH', 'name': 'HCL Technologies Ltd.'},
    {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd.'},
    {'symbol': 'HDFCLIFE', 'name': 'HDFC Life Insurance Company Ltd.'},
    {'symbol': 'HEROMOTOCO', 'name': 'Hero MotoCorp Ltd.'},
    {'symbol': 'HINDALCO', 'name': 'Hindalco Industries Ltd.'},
    {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd.'},
    {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.'},
    {'symbol': 'INDUSINDBK', 'name': 'IndusInd Bank Ltd.'},
    {'symbol': 'INFY', 'name': 'Infosys Ltd.'},
    {'symbol': 'ITC', 'name': 'ITC Ltd.'},
    {'symbol': 'JSWSTEEL', 'name': 'JSW Steel Ltd.'},
    {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd.'},
    {'symbol': 'LT', 'name': 'Larsen & Toubro Ltd.'},
    {'symbol': 'M&M', 'name': 'Mahindra & Mahindra Ltd.'},
    {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd.'},
    {'symbol': 'NESTLEIND', 'name': 'Nestle India Ltd.'},
    {'symbol': 'NTPC', 'name': 'NTPC Ltd.'},
    {'symbol': 'ONGC', 'name': 'Oil and Natural Gas Corporation Ltd.'},
    {'symbol': 'POWERGRID', 'name': 'Power Grid Corporation of India Ltd.'},
    {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.'},
    {'symbol': 'SBILIFE', 'name': 'SBI Life Insurance Company Ltd.'},
    {'symbol': 'SBIN', 'name': 'State Bank of India'},
    {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical Industries Ltd.'},
    {'symbol': 'TATACONSUM', 'name': 'Tata Consumer Products Ltd.'},
    {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd.'},
    {'symbol': 'TATASTEEL', 'name': 'Tata Steel Ltd.'},
    {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.'},
    {'symbol': 'TECHM', 'name': 'Tech Mahindra Ltd.'},
    {'symbol': 'TITAN', 'name': 'Titan Company Ltd.'},
    {'symbol': 'ULTRACEMCO', 'name': 'UltraTech Cement Ltd.'},
    {'symbol': 'WIPRO', 'name': 'Wipro Ltd.'},
    {'symbol': 'ADANIENT', 'name': 'Adani Enterprises Ltd.'},
    {'symbol': 'LTIM', 'name': 'LTIMindtree Ltd.'},
    {'symbol': 'SHRIRAMFIN', 'name': 'Shriram Finance Ltd.'}
]

def g_res(sym, iss, ped):
    """Get results from NSE API - automatically chooses the right API based on date"""
    s = requests.Session()
    s.headers.update(h)
    
    # Determine which API to use based on period
    if ped in INTEGRATED_FILING_QUARTERS:
        # Use integrated filing API for 2025 data
        url = u_if
        q = {
            "index": "equities",
            "symbol": sym,
            "issuer": iss,
            "period_ended": ped,
            "type": "Integrated Filing- Financials",
            "page": 1,
            "size": 20
        }
    else:
        # Use older financial results API for pre-2025 data
        url = u_old
        q = {
            "index": "equities",
            "symbol": sym,
            "issuer": iss,
            "period": ped,
            "page": 1,
            "size": 20
        }
    
    try:
        # First visit the main page to get cookies
        s.get("https://www.nseindia.com", timeout=10)
        
        # Then make the API request
        r = s.get(url, params=q, timeout=20)
        r.raise_for_status()
        return r.json(), s
    except requests.exceptions.RequestException as e:
        print(f"  API Error: {str(e)}")
        return {}, s

def dl_all(sym, iss, ped, filing_type='both'):
    """Download XBRL files for a company
    
    filing_type: 'consolidated', 'standalone', or 'both'
    ped: period in format like '31-Dec-2024' or '30-Jun-2025'
    """
    try:
        print(f"\n--- Fetching {sym} for {ped} ---")
        j, s = g_res(sym, iss, ped)
        
        # Handle both API response formats
        # New API returns: {"data": [...]}
        # Old API returns: [...] directly or {"data": [...]}
        if isinstance(j, dict):
            xs = j.get("data", [])
        elif isinstance(j, list):
            xs = j
        else:
            xs = []
        
        print(f"API returned {len(xs)} items")
        
        if not xs:
            return {'success': False, 'message': f'No filings found'}
        
        # Normalize input period to match API response format
        target_date = ped
        target_date_upper = ped.upper()
        
        files_downloaded = []
        matching_items = []
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # First pass: collect all matching date items
        for item in xs:
            if not isinstance(item, dict):
                continue
                
            r = item
            api_to_date = r.get("toDate") or r.get("qe_Date") or ""
            api_date_normalized = api_to_date.upper()
            
            # Only collect items that match the selected quarter end date
            if api_date_normalized == target_date_upper:
                matching_items.append(r)
        
        if not matching_items:
            return {'success': False, 'message': f'No filings found for date {target_date_upper}'}
        
        print(f"Found {len(matching_items)} filings for {target_date_upper}")
        
        # Check what types are available
        consolidated_available = any('consolidated' in (r.get("consolidated") or "").lower() and 
                                    'non' not in (r.get("consolidated") or "").lower() 
                                    for r in matching_items)
        standalone_available = any('non' in (r.get("consolidated") or "").lower() or
                                  'standalone' in (r.get("consolidated") or "").lower()
                                  for r in matching_items)
        
        print(f"Available: Consolidated={consolidated_available}, Standalone={standalone_available}")
        
        # Adjust filing_type if requested type not available
        if filing_type == 'consolidated' and not consolidated_available and standalone_available:
            print(f"⚠ Consolidated not available, downloading standalone instead")
            filing_type = 'standalone'
        elif filing_type == 'standalone' and not standalone_available and consolidated_available:
            print(f"⚠ Standalone not available, downloading consolidated instead")
            filing_type = 'consolidated'
        
        # Second pass: download files
        for r in matching_items:
            api_to_date = r.get("toDate") or r.get("qe_Date") or ""
            filing_type_from_api = (r.get("consolidated") or "").lower()
            
            # Handle both "Consolidated"/"Standalone" and "Consolidated"/"Non-Consolidated"
            is_consolidated = 'consolidated' in filing_type_from_api and 'non' not in filing_type_from_api
            
            if filing_type == 'consolidated' and not is_consolidated:
                print(f"  Skipping non-consolidated: {filing_type_from_api}")
                continue
            elif filing_type == 'standalone' and is_consolidated:
                print(f"  Skipping consolidated: {filing_type_from_api}")
                continue
            # if filing_type == 'both', download all
            
            print(f"  ✓ Downloading {filing_type_from_api} filing")
            
            x = r.get("xbrl")
            if not x:
                print(f"  ✗ No XBRL URL found")
                continue
                
            z = s.get(x, timeout=30, allow_redirects=True)
            ct = z.headers.get("content-type", "")
            if z.status_code != 200 or "xml" not in ct.lower():
                print(f"  ✗ Invalid response: status={z.status_code}, content-type={ct}")
                continue
            
            tag = (r.get("consolidated") or "NA").replace(" ", "_")
            qe = (api_to_date or "").replace(" ", "_")
            nm = f"{sym}_{qe}_{tag}.xml"
            pth = os.path.join(app.config['UPLOAD_FOLDER'], nm)
            with open(pth, "wb") as f:
                f.write(z.content)
            files_downloaded.append(nm)
            print(f"  ✓ Saved: {nm}")
        
        if files_downloaded:
            return {'success': True, 'message': f'Downloaded {len(files_downloaded)} file(s)', 'files': files_downloaded}
        else:
            return {'success': False, 'message': f'No matching filings found for {target_date_upper}'}
    
    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return {'success': False, 'message': f'Error: {str(e)}'}

def download_in_background(companies_list, period, filing_type='both'):
    """Download files in background"""
    global download_progress
    download_progress = {'status': 'downloading', 'message': 'Starting downloads...', 'files': [], 'errors': []}
    
    total = len(companies_list)
    success_count = 0
    
    for i, company in enumerate(companies_list):
        try:
            download_progress['message'] = f'Downloading {company["symbol"]} ({i+1}/{total})...'
            download_progress['current'] = i + 1
            download_progress['total'] = total
            
            result = dl_all(company['symbol'], company['name'], period, filing_type)
            if result['success']:
                download_progress['files'].extend(result.get('files', []))
                success_count += 1
                print(f"✓ [{i+1}/{total}] {company['symbol']}: {result['message']}")
            else:
                download_progress['errors'].append(f"{company['symbol']}: {result['message']}")
                print(f"✗ [{i+1}/{total}] {company['symbol']}: {result['message']}")
            
            # Add small delay between requests to avoid rate limiting
            if i < total - 1:  # Don't delay after last request
                time.sleep(0.5)
                
        except Exception as e:
            error_msg = f"{company['symbol']}: {str(e)}"
            download_progress['errors'].append(error_msg)
            print(f"✗ [{i+1}/{total}] Error: {error_msg}")
    
    download_progress['status'] = 'completed'
    download_progress['message'] = f'Completed! Downloaded {len(download_progress["files"])} files from {success_count}/{total} stocks'
    print(f"\n=== Download Complete ===")
    print(f"Files downloaded: {len(download_progress['files'])}")
    print(f"Stocks processed: {success_count}/{total}")
    print(f"Errors: {len(download_progress['errors'])}")

@app.route('/')
def index():
    return render_template('index.html', companies=NIFTY50)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    symbols = data.get('symbols', [])
    period = data.get('period', '')
    filing_type = data.get('filingType', 'both')
    
    if not symbols or not period:
        return jsonify({'success': False, 'message': 'Please select stocks and period'}), 400
    
    # Find company details
    companies_to_download = []
    for sym in symbols:
        company = next((c for c in NIFTY50 if c['symbol'] == sym), None)
        if company:
            companies_to_download.append(company)
    
    # Start download in background
    thread = threading.Thread(target=download_in_background, args=(companies_to_download, period, filing_type))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Download started'})

@app.route('/api/progress', methods=['GET'])
def progress():
    return jsonify(download_progress)

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'files': [], 'error': str(e)})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
