"""
qoq_cr_single_row.py

Reads XBRL/XML files from xbrl_downloads folder (3 files per stock),
converts values to Crores (Cr), calculates QoQ% and YoY%,
and outputs everything in a single Excel file with one row per stock.

Columns:
StockSymbol | CompanyName | Metric (Cr) | Metric QoQ% | Metric YoY% ...
"""

import os
import glob
from lxml import etree
import pandas as pd
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# ---------------------------
# CONFIGURE YOUR FILE PATHS
# Automatically find XBRL files in the xbrl_downloads folder
# ---------------------------

DOWNLOADS_FOLDER = os.path.join(os.path.dirname(__file__), "xbrl_downloads")

# Find all XML files in the downloads folder
xml_files = glob.glob(os.path.join(DOWNLOADS_FOLDER, "*.xml"))

if len(xml_files) < 3:
    raise FileNotFoundError(f"Expected at least 3 XML files in {DOWNLOADS_FOLDER}, found {len(xml_files)}")

print(f"Found {len(xml_files)} XML files in {DOWNLOADS_FOLDER}")

# Group files by stock symbol (extract from filename or parse from XML)
# We'll parse each file to get the stock symbol, then group them
# ---------------------------


# OUTPUT LOCATION
OUTPUT_XLSX = os.path.join(DOWNLOADS_FOLDER, "financial_comparison_all_stocks.xlsx")

# MongoDB Configuration (from .env file)
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "financial_data")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "quarterly_results")

# Build MongoDB URI with URL-encoded password
if MONGODB_USERNAME and MONGODB_PASSWORD and MONGODB_CLUSTER:
    password_encoded = urllib.parse.quote_plus(MONGODB_PASSWORD)
    MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{password_encoded}@{MONGODB_CLUSTER}/?appName=Cluster0"
else:
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")


# Aliases for tag names (add more if needed)
TAG_ALIASES = {
    "revenue": ["RevenueFromOperations", "TotalRevenue", "Revenue", "Income", "SegmentRevenueFromOperations"],
    "profit_before_exceptional_and_tax": ["ProfitBeforeExceptionalItemsAndTax", "ProfitBeforeTax", "ProfitBeforeExtraordinaryItemsAndTax", "ProfitLossFromOrdinaryActivitiesBeforeTax"],
    "depreciation": ["DepreciationDepletionAndAmortisationExpense", "Depreciation"],
    "finance_costs": ["FinanceCosts", "FinanceCost"],
    "net_profit": ["ProfitLossForPeriod", "ProfitOrLoss", "ProfitLossForThePeriod", "ProfitLossFromOrdinaryActivitiesAfterTax"],
    "basic_eps": ["BasicEarningsLossPerShareFromContinuingAndDiscontinuedOperations", "BasicEarningsLossPerShare", "BasicEPS", "BasicEarningsPerShareBeforeExtraordinaryItems", "BasicEarningsPerShareAfterExtraordinaryItems"],
    "cashflow_operating": ["CashFlowsFromUsedInOperatingActivities", "CashFlowFromOperatingActivities", "NetCashFlowFromOperatingActivities"],
    "borrowings": ["TotalBorrowings", "Borrowings"],
    "borrowings_noncurrent": ["BorrowingsNoncurrent"],
    "borrowings_current": ["BorrowingsCurrent"],
    "exceptional": ["ExceptionalItemsBeforeTax", "ExceptionalItems"],
    "company_name": ["EntityRegistrantName", "CompanyName", "NameOfTheCompany", "NameOfBank", "NameOfTheEntity"],
    "stock_symbol": ["TradingSymbol", "StockExchangeSymbol", "Symbol"]
}

SEGMENT_REVENUE_TAG = "SegmentRevenue"

WC_TAGS = [
    "AdjustmentsForDecreaseIncreaseInInventories",
    "AdjustmentsForDecreaseIncreaseInTradeReceivablesCurrent",
    "AdjustmentsForIncreaseDecreaseInTradePayablesCurrent",
    "AdjustmentsForIncreaseDecreaseInOtherCurrentLiabilities",
    "AdjustmentsForDecreaseIncreaseInOtherCurrentAssets"
]

# ---------------------------
# Helper functions
# ---------------------------

def parse_number(text):
    if not text:
        return None
    t = text.replace(",", "").replace(" ", "")
    t = t.replace("(", "-").replace(")", "")
    t = t.replace("\u2212", "-")
    try:
        return float(t)
    except:
        return None

def to_cr(val):
    if val is None:
        return None
    return val / 1e7

def pct_change(curr, base):
    if base is None or base == 0:
        return None
    return (curr - base) / base * 100

def pick_tag_value(dct, aliases):
    for a in aliases:
        if a in dct:
            return dct[a]
    return None

# ---------------------------
# Parse XBRL/XML File
# ---------------------------

def parse_xbrl_file(path):
    tree = etree.parse(path)
    root = tree.getroot()

    # contexts
    contexts = {}
    for ctx in root.findall(".//{http://www.xbrl.org/2003/instance}context"):
        cid = ctx.get("id")
        end = ctx.find(".//{http://www.xbrl.org/2003/instance}endDate")
        inst = ctx.find(".//{http://www.xbrl.org/2003/instance}instant")
        if end is not None:
            contexts[cid] = end.text
        elif inst is not None:
            contexts[cid] = inst.text

    values_by_context = {}
    texts = {}

    for elem in root.iter():
        tag = etree.QName(elem.tag).localname
        txt = elem.text.strip() if elem.text else None

        # Save company name / symbol
        if txt:
            if tag in TAG_ALIASES["company_name"]:
                texts["company_name"] = txt
            if tag in TAG_ALIASES["stock_symbol"]:
                texts["stock_symbol"] = txt

        # Numeric values
        num = parse_number(txt)
        if num is not None:
            ctxref = elem.get("contextRef")
            if ctxref:
                values_by_context.setdefault(ctxref, {})[tag] = num

    # Pick best context - prefer quarterly (OneD, TwoD, ThreeD) over cumulative (FourD)
    if not values_by_context:
        return {"values": {}, "texts": texts, "chosen_date": None}

    # Categorize contexts
    quarterly_contexts = []
    cumulative_contexts = []
    other_contexts = []
    
    for context_id, vals in values_by_context.items():
        count = len(vals)
        ctx_lower = context_id.lower()
        
        # OneD, TwoD, ThreeD are quarterly (3-month periods)
        if ctx_lower in ['oned', 'twod', 'threed']:
            quarterly_contexts.append((context_id, count, vals))
        # FourD is cumulative (6 or 9-month period)
        elif ctx_lower == 'fourd':
            cumulative_contexts.append((context_id, count, vals))
        else:
            other_contexts.append((context_id, count, vals))
    
    # First try quarterly contexts
    if quarterly_contexts:
        quarterly_contexts.sort(key=lambda x: x[1], reverse=True)
        best_context = quarterly_contexts[0][0]
        best_vals = quarterly_contexts[0][2]
    # Fall back to cumulative if no quarterly found
    elif cumulative_contexts:
        cumulative_contexts.sort(key=lambda x: x[1], reverse=True)
        best_context = cumulative_contexts[0][0]
        best_vals = cumulative_contexts[0][2]
    # Fall back to any other context
    elif other_contexts:
        other_contexts.sort(key=lambda x: x[1], reverse=True)
        best_context = other_contexts[0][0]
        best_vals = other_contexts[0][2]
    else:
        return {"values": {}, "texts": texts, "chosen_date": None}
    
    chosen_date = contexts.get(best_context, "")
    
    # Also collect from OneI (instant/balance sheet items like Borrowings)
    instant_context = best_context.replace('D', 'I') if 'D' in best_context else 'OneI'
    if instant_context in values_by_context:
        # Merge instant values (balance sheet items)
        for tag, val in values_by_context[instant_context].items():
            if tag not in best_vals:
                best_vals[tag] = val
    
    # For cash flow, use FourD since it's not available in quarterly contexts
    # Note: FourD for Q1 = 3 months, FourD for Q2 = 6 months (cumulative)
    if 'FourD' in values_by_context:
        for tag in ['CashFlowsFromUsedInOperatingActivities', 'CashFlowFromOperatingActivities', 'NetCashFlowFromOperatingActivities']:
            if tag in values_by_context['FourD'] and tag not in best_vals:
                best_vals[tag] = values_by_context['FourD'][tag]
    
    return {"values": best_vals, "texts": texts, "chosen_date": chosen_date}

# ---------------------------
# MAIN EXECUTION
# ---------------------------

# First pass: parse all files and group by stock symbol
print("Parsing all XBRL files...")
files_by_stock = defaultdict(list)

for xml_file in xml_files:
    info = parse_xbrl_file(xml_file)
    stock_symbol = info["texts"].get("stock_symbol") or "UNKNOWN"
    
    files_by_stock[stock_symbol].append({
        "path": xml_file,
        "values": info["values"],
        "texts": info["texts"],
        "date": info["chosen_date"]
    })

print(f"Found {len(files_by_stock)} unique stocks")

# Sort oldest → newest
def parse_date(s):
    try:
        return datetime.fromisoformat(s).date()
    except:
        return datetime(2000, 1, 1).date()

def date_to_quarter(date_str):
    """Convert date string (YYYY-MM-DD) to Indian Financial Year Quarter notation"""
    try:
        d = datetime.fromisoformat(date_str).date()
        month = d.month
        year = d.year
        
        # Indian Financial Year: Apr-Mar
        # Apr-Jun: Q1, Jul-Sep: Q2, Oct-Dec: Q3, Jan-Mar: Q4
        if month >= 4:  # Apr onwards
            quarter = (month - 4) // 3 + 1
            fy = year + 1  # FY2025 = Apr 2024 - Mar 2025
        else:  # Jan-Mar
            quarter = 4
            fy = year
        
        return f"Q{quarter} FY{fy}"
    except:
        return "Unknown"

# Process each stock
all_rows = []

for stock_symbol, parsed_files in files_by_stock.items():
    # Sort by date (oldest to newest)
    parsed = sorted(parsed_files, key=lambda x: parse_date(x["date"] or ""))
    
    # We need exactly 3 files per stock
    if len(parsed) != 3:
        print(f"Warning: {stock_symbol} has {len(parsed)} files (expected 3), skipping...")
        continue
    
    prev_year, prev_q, current = parsed

    # Extract company name / symbol
    company_name = current["texts"].get("company_name") or "Unknown"
    stock_symbol = current["texts"].get("stock_symbol") or "UNKNOWN"

    cv = current["values"]
    pqv = prev_q["values"]
    pyv = prev_year["values"]

    def get_val(dictionary, key):
        return pick_tag_value(dictionary, TAG_ALIASES[key])

    # Extract metrics
    revenue_c = get_val(cv, "revenue")
    revenue_pq = get_val(pqv, "revenue")
    revenue_py = get_val(pyv, "revenue")

    pbt_c = get_val(cv, "profit_before_exceptional_and_tax")
    pbt_pq = get_val(pqv, "profit_before_exceptional_and_tax")
    pbt_py = get_val(pyv, "profit_before_exceptional_and_tax")

    dep_c = get_val(cv, "depreciation")
    dep_pq = get_val(pqv, "depreciation")
    dep_py = get_val(pyv, "depreciation")

    fin_c = get_val(cv, "finance_costs")
    fin_pq = get_val(pqv, "finance_costs")
    fin_py = get_val(pyv, "finance_costs")

    np_c = get_val(cv, "net_profit")
    np_pq = get_val(pqv, "net_profit")
    np_py = get_val(pyv, "net_profit")

    eps_c = get_val(cv, "basic_eps")
    eps_pq = get_val(pqv, "basic_eps")
    eps_py = get_val(pyv, "basic_eps")

    cf_c = get_val(cv, "cashflow_operating")
    cf_pq = get_val(pqv, "cashflow_operating")
    cf_py = get_val(pyv, "cashflow_operating")

    bor_c = get_val(cv, "borrowings")
    bor_pq = get_val(pqv, "borrowings")
    bor_py = get_val(pyv, "borrowings")

    # If total borrowings not found, try to combine current + noncurrent
    if bor_c is None:
        noncurr_c = get_val(cv, "borrowings_noncurrent")
        curr_c = get_val(cv, "borrowings_current")
        if noncurr_c is not None or curr_c is not None:
            bor_c = (noncurr_c or 0) + (curr_c or 0)

    if bor_pq is None:
        noncurr_pq = get_val(pqv, "borrowings_noncurrent")
        curr_pq = get_val(pqv, "borrowings_current")
        if noncurr_pq is not None or curr_pq is not None:
            bor_pq = (noncurr_pq or 0) + (curr_pq or 0)

    if bor_py is None:
        noncurr_py = get_val(pyv, "borrowings_noncurrent")
        curr_py = get_val(pyv, "borrowings_current")
        if noncurr_py is not None or curr_py is not None:
            bor_py = (noncurr_py or 0) + (curr_py or 0)

    exc_c = get_val(cv, "exceptional")
    exc_pq = get_val(pqv, "exceptional")
    exc_py = get_val(pyv, "exceptional")

    # EBITDA
    ebitda_c = (pbt_c or 0) + (dep_c or 0) + (fin_c or 0)
    ebitda_pq = (pbt_pq or 0) + (dep_pq or 0) + (fin_pq or 0)
    ebitda_py = (pbt_py or 0) + (dep_py or 0) + (fin_py or 0)

    # Margins (%)
    def margin(numer, denom):
        if numer is None or denom is None or denom == 0:
            return None
        return (numer / denom) * 100

    ebm_c = margin(ebitda_c, revenue_c)
    ebm_pq = margin(ebitda_pq, revenue_pq)
    ebm_py = margin(ebitda_py, revenue_py)

    npm_c = margin(np_c, revenue_c)
    npm_pq = margin(np_pq, revenue_pq)
    npm_py = margin(np_py, revenue_py)

    # Build row
    row = {
        "StockSymbol": stock_symbol,
        "CompanyName": company_name
    }

    # Helper to add 3 columns per metric
    def add(prefix, c, pq, py, cr=True):
        # Get quarter labels from dates
        current_q = date_to_quarter(current["date"])
        prev_q_label = date_to_quarter(prev_q["date"])
        prev_year_q = date_to_quarter(prev_year["date"])
        
        row[f"{prefix} {current_q} (Cr)" if cr else f"{prefix} {current_q}"] = to_cr(c) if cr else c
        row[f"{prefix} {prev_q_label} (Cr)" if cr else f"{prefix} {prev_q_label}"] = to_cr(pq) if cr else pq
        row[f"{prefix} {prev_year_q} (Cr)" if cr else f"{prefix} {prev_year_q}"] = to_cr(py) if cr else py
        row[f"{prefix} QoQ%"] = pct_change(c, pq)
        row[f"{prefix} YoY%"] = pct_change(c, py)

    add("Revenue", revenue_c, revenue_pq, revenue_py)
    add("EBITDA", ebitda_c, ebitda_pq, ebitda_py)
    row["EBITDA Margin (%)"] = ebm_c
    row["EBITDA Margin QoQ (pp)"] = (ebm_c - ebm_pq) if ebm_c and ebm_pq else None
    row["EBITDA Margin YoY (pp)"] = (ebm_c - ebm_py) if ebm_c and ebm_py else None

    add("Net Profit", np_c, np_pq, np_py)
    row["Net Profit Margin (%)"] = npm_c
    row["Net Profit Margin QoQ (pp)"] = (npm_c - npm_pq) if npm_c and npm_pq else None
    row["Net Profit Margin YoY (pp)"] = (npm_c - npm_py) if npm_c and npm_py else None

    add("Basic EPS", eps_c, eps_pq, eps_py, cr=False)
    add("Cash Flow from Ops", cf_c, cf_pq, cf_py)
    add("Borrowings", bor_c, bor_pq, bor_py)
    add("Finance Costs", fin_c, fin_pq, fin_py)
    add("Exceptional Items", exc_c, exc_pq, exc_py)
    
    all_rows.append(row)
    print(f"  Processed: {stock_symbol} - {company_name}")

# Make DataFrame
df = pd.DataFrame(all_rows)

# Ensure directory exists
os.makedirs(os.path.dirname(OUTPUT_XLSX), exist_ok=True)

df.to_excel(OUTPUT_XLSX, index=False)

print(f"\nSaved Excel with {len(all_rows)} stocks to: {OUTPUT_XLSX}")

# ---------------------------
# UPLOAD TO MONGODB
# ---------------------------

def upload_to_mongodb(data_rows):
    """Upload financial data to MongoDB"""
    try:
        # Connect to MongoDB
        print(f"\nConnecting to MongoDB at {MONGODB_URI.split('@')[1].split('?')[0]}...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("[OK] Connected to MongoDB successfully")
        
        # Get database and collection
        db = client[MONGODB_DATABASE]
        collection = db[MONGODB_COLLECTION]
        
        # Convert DataFrame rows to documents
        documents = []
        for row in data_rows:
            # Convert NaN values to None for MongoDB
            doc = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            
            # Add metadata
            doc['uploaded_at'] = datetime.now()
            doc['data_source'] = 'XBRL'
            
            documents.append(doc)
        
        # Clear existing data for these stocks (optional - comment out to keep history)
        stock_symbols = [doc['StockSymbol'] for doc in documents]
        result = collection.delete_many({'StockSymbol': {'$in': stock_symbols}})
        print(f"[OK] Deleted {result.deleted_count} existing records")
        
        # Insert new data
        result = collection.insert_many(documents)
        print(f"[OK] Uploaded {len(result.inserted_ids)} records to MongoDB")
        print(f"  Database: {MONGODB_DATABASE}")
        print(f"  Collection: {MONGODB_COLLECTION}")
        
        return True
        
    except ConnectionFailure:
        print("[ERROR] Failed to connect to MongoDB. Check your credentials.")
        print(f"  Cluster: {MONGODB_CLUSTER}")
        return False
    except Exception as e:
        print(f"[ERROR] Error uploading to MongoDB: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

# Upload to MongoDB
print("\n" + "="*80)
print("UPLOADING TO MONGODB")
print("="*80)
upload_to_mongodb(all_rows)
