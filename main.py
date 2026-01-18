# main.py

from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data 
)
from utils.report_generator import generate_sales_report



import os

DATA_FILE = os.path.join("data", "sales_data.txt")


def main():
    print("Starting Sales Analytics System (Q2)...\n")

    raw_lines = read_sales_data(DATA_FILE)
    transactions = parse_transactions(raw_lines)

    valid, invalid_count, summary = validate_and_filter(
        transactions,
        region=None,        # example: "North"
        min_amount=None,    # example: 5000
        max_amount=None     # example: 100000
    )

    print("\nValidation Summary:")
    for k, v in summary.items():
        print(f"{k}: {v}")


    print("\n========== Q3 TESTING ==========\n")

    # Total Revenue
    total_revenue = calculate_total_revenue(valid)
    print(f"Total Revenue: {total_revenue}")

    # Region-wise Sales
    print("\nRegion-wise Sales:")
    region_sales = region_wise_sales(valid)
    for region, data in region_sales.items():
        print(region, data)

    # Top Selling Products
    print("\nTop Selling Products:")
    for product in top_selling_products(valid):
        print(product)

    # Customer Analysis (show top 5 only)
    print("\nTop Customers:")
    customers = customer_analysis(valid)
    count = 0
    for cid, info in customers.items():
        print(cid, info)
        count += 1
        if count == 5:
            break

    # Daily Sales Trend (first 5 days)
    print("\nDaily Sales Trend:")
    daily_trend = daily_sales_trend(valid)
    count = 0
    for date, info in daily_trend.items():
        print(date, info)
        count += 1
        if count == 5:
            break

    # Find peak salesday
    print("\nPeak Sales Day:")
    peak_day = find_peak_sales_day(valid)
    print(peak_day)

    # Test Low Performing Products
    print("\nTesting Low Performing Products:")
    low_products = low_performing_products(valid, threshold=10)
    if low_products:
        for product in low_products:
            print(product)
    else:
        print("No low performing products found.")

    # -----------------------------
    # Q4: API Integration – Step 3.1 (a)
    # -----------------------------
    print("\nTesting API Fetch:")
    api_products = fetch_all_products()
    print("Number of products fetched:", len(api_products))

    print("\nFirst 3 API Products:")
    for p in api_products[:3]:
        print(p)

    # -----------------------------
    # Q4: API Integration – Step 3.1 (b)
    # -----------------------------

    print("\nFetching products from DummyJSON API...")
    api_products = fetch_all_products()   # ✅ THIS LINE WAS MISSING

    print("Total products fetched:", len(api_products))

    print("\nTesting Product Mapping:")
    product_mapping = create_product_mapping(api_products)

    print("Total mapped products:", len(product_mapping))

    count = 0
    for pid, info in product_mapping.items():
        print(pid, info)
        count += 1
        if count == 3:
           break

    # -----------------------------
    # Q4: API Integration – Step 3.2
    # -----------------------------

    print("DEBUG: valid count =", len(valid))

    # Step 5: Enrich transactions
    enriched_data = enrich_sales_data(valid, product_mapping)
    print(f"\nEnriched {len(enriched_data)} transactions")

    # Step 6: Save enriched transactions
    save_enriched_data(enriched_data)
    print("\nEnriched sales data saved to 'data/enriched_sales_data.txt'")

    # -----------------------------
    # Q4: API Integration – Step 3.2
    # -----------------------------
    
    generate_sales_report(valid, enriched_data)

    # -----------------------------
    # Q6: Main Application – 
    # -----------------------------
    """
    Main execution function
    """

    try:
        print("="*40)
        print("       SALES ANALYTICS SYSTEM")
        print("="*40 + "\n")

        # Step 1 & 2: Read and parse data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data(DATA_FILE)
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records\n")

        # Step 3 & 4: Show filter options
        regions = sorted(set(t['Region'] for t in transactions))
        amounts = [t['Quantity'] * t['UnitPrice'] for t in transactions]
        min_amount, max_amount = min(amounts), max(amounts)

        print("[3/10] Filter Options Available:")
        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ₹{min_amount:,.0f} - ₹{max_amount:,.0f}\n")

        filter_choice = input("Do you want to filter data? (y/n): ").strip().lower()

        # Step 5: Apply filters if chosen
        filtered_transactions = transactions
        if filter_choice == 'y':
            region_input = input("Enter region to filter (or leave blank for all): ").strip()
            if region_input:
                filtered_transactions = [
                    t for t in filtered_transactions if t['Region'].lower() == region_input.lower()
                ]

            min_input = input(f"Enter minimum transaction amount (or leave blank for {min_amount}): ").strip()
            if min_input:
                min_input = float(min_input)
                filtered_transactions = [
                    t for t in filtered_transactions if t['Quantity'] * t['UnitPrice'] >= min_input
                ]

            max_input = input(f"Enter maximum transaction amount (or leave blank for {max_amount}): ").strip()
            if max_input:
                max_input = float(max_input)
                filtered_transactions = [
                    t for t in filtered_transactions if t['Quantity'] * t['UnitPrice'] <= max_input
                ]

            print(f"\n✓ Filter applied. {len(filtered_transactions)} transactions remaining.\n")
        else:
            print("✓ No filter applied.\n")

        # Step 6: Validate transactions
        print("[4/10] Validating transactions...")
        valid, invalid_count, summary = validate_and_filter(
            filtered_transactions,
            region=None,
            min_amount=None,
            max_amount=None
        )
        print(f"✓ Valid: {len(valid)} | Invalid: {invalid_count}\n")

        # Step 7: Perform data analyses (already in report functions)
        print("[5/10] Analyzing sales data...")
        # You can call your analysis functions here if needed for console feedback
        _ = region_wise_sales(valid)
        _ = top_selling_products(valid, n=5)
        _ = customer_analysis(valid)
        _ = daily_sales_trend(valid)
        _ = low_performing_products(valid)
        print("✓ Analysis complete\n")

        # Step 8: Fetch products from API
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products\n")

        # Step 9: Enrich sales data
        print("[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid, product_mapping)
        enriched_count = sum(1 for t in enriched_transactions if t.get('API_Match'))
        success_rate = (enriched_count / len(valid) * 100) if valid else 0
        print(f"✓ Enriched {enriched_count}/{len(valid)} transactions ({success_rate:.1f}%)\n")

        # Step 10: Save enriched data
        print("[8/10] Saving enriched data...")
        enriched_file = 'data/enriched_sales_data.txt'
        save_enriched_data(enriched_transactions, filename=enriched_file)
        print(f"✓ Saved to: {enriched_file}\n")

        # Step 11: Generate report
        print("[9/10] Generating report...")
        report_file = 'output/sales_report.txt'
        generate_sales_report(valid, enriched_transactions, output_file=report_file)
        print(f"✓ Report saved to: {report_file}\n")

        print("[10/10] Process Complete!")
        print("="*40)


    except FileNotFoundError:
        print("\n❌ Sales data file not found. Please check the data folder.")

    except Exception as e:
        print("\n❌ An unexpected error occurred")
        print("Error:", e)





if __name__ == "__main__":
    main()
