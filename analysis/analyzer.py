# analyzer.py (updated)
import pandas as pd
from typing import Dict, List, Any

def analyze_data(scraped_data: Dict[str, List[Any]]) -> Dict[str, pd.DataFrame]:
    combined = []
    for source, products in scraped_data.items():
        if not products:  # Skip empty results
            continue
            
        for product in products:
            # Handle both GlobalGolf and RockBottom formats
            if source == "globalgolf":
                # Format: [page, name, price, brand, link, offer]
                combined.append([
                    source,
                    product[0],  # page
                    product[1],  # name
                    product[2],  # price
                    product[3],  # brand
                    product[4],  # url
                    product[5] if len(product) > 5 else "N/A"  # offer
                ])
            elif source == "rockbottom":
                # Format: [page, name, price, brand, link]
                combined.append([
                    source,
                    product[0],  # page
                    product[1],  # name
                    product[2],  # price
                    product[3],  # brand
                    product[4],  # url
                    "N/A"  # offer
                ])

    columns = ["Source", "Page", "Name", "Price", "Brand", "URL", "Offer/Savings"]
    raw_df = pd.DataFrame(combined, columns=columns)

    # Clean and convert prices
    raw_df["Price"] = raw_df["Price"].astype(str).str.replace(r'[^0-9.]', '', regex=True)
    raw_df["Price"] = pd.to_numeric(raw_df["Price"], errors='coerce')
    raw_df.dropna(subset=["Price"], inplace=True)

    # Calculate stats separately for each source
    stats_dfs = []
    for source in scraped_data.keys():
        source_df = raw_df[raw_df["Source"] == source]
        if not source_df.empty:
            source_stats = source_df.groupby("Brand").agg(
                Average_Price=("Price", "mean"),
                Min_Price=("Price", "min"),
                Max_Price=("Price", "max"),
                Product_Count=("Price", "count")
            ).round(2).reset_index()
            source_stats["Source"] = source
            stats_dfs.append(source_stats)
    
    stats_df = pd.concat(stats_dfs) if stats_dfs else pd.DataFrame()

    # Identify best deals across all sources
    if not stats_df.empty:
        best_deals = stats_df.sort_values("Min_Price").head(10)
    else:
        best_deals = pd.DataFrame()

    # Top brands by volume across all sources
    top_brands = (
        raw_df["Brand"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Brand", "Brand": "Product_Count"})
        .head(10)
    )

    # Most expensive listings across all sources
    top_expensive = raw_df.sort_values(by="Price", ascending=False).head(10)

    return {
        "raw_data": raw_df,
        "stats": stats_df,
        "top_brands": top_brands,
        "top_expensive": top_expensive
    }