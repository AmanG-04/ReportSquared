import argparse
import os
from datetime import datetime

import pandas as pd
from pymongo import MongoClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Import quarterly financial XLSX data into MongoDB for the stock API."
    )
    parser.add_argument("--file", required=True, help="Path to XLSX file")
    parser.add_argument("--sheet", default=0, help="Sheet name or index (default: first sheet)")
    parser.add_argument(
        "--mongo-uri",
        default=os.getenv("MONGODB_LOCAL_URI") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017",
        help="MongoDB URI (default: MONGODB_LOCAL_URI, then MONGODB_URI, then mongodb://localhost:27017)",
    )
    parser.add_argument(
        "--database",
        default=os.getenv("MONGODB_DATABASE", "stocks"),
        help="MongoDB database name",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("MONGODB_COLLECTION", "quarterly_results"),
        help="MongoDB collection name",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing collection data before import",
    )
    return parser.parse_args()


def normalize_doc(record):
    doc = {}
    for key, value in record.items():
        if pd.isna(value):
            doc[key] = None
        elif isinstance(value, pd.Timestamp):
            doc[key] = value.to_pydatetime()
        else:
            doc[key] = value
    doc["imported_at"] = datetime.utcnow()
    return doc


def main():
    args = parse_args()

    if not os.path.exists(args.file):
        raise FileNotFoundError(f"XLSX not found: {args.file}")

    df = pd.read_excel(args.file, sheet_name=args.sheet)
    if df.empty:
        raise ValueError("XLSX sheet is empty")

    records = df.to_dict(orient="records")
    documents = [normalize_doc(r) for r in records]

    client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    collection = client[args.database][args.collection]

    if args.replace:
        collection.delete_many({})

    # Use StockSymbol upsert when available to avoid duplicates across reruns.
    if "StockSymbol" in df.columns:
        upserted = 0
        modified = 0
        for doc in documents:
            symbol = doc.get("StockSymbol")
            if symbol:
                result = collection.update_one(
                    {"StockSymbol": symbol},
                    {"$set": doc},
                    upsert=True,
                )
                upserted += int(result.upserted_id is not None)
                modified += result.modified_count
            else:
                collection.insert_one(doc)
        print(f"Imported {len(documents)} rows with StockSymbol upsert")
        print(f"Upserted: {upserted}, Modified: {modified}")
    else:
        result = collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} rows")

    print(f"Database: {args.database}")
    print(f"Collection: {args.collection}")


if __name__ == "__main__":
    main()
