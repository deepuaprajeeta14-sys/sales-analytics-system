from datetime import datetime

from utils.data_processor import (
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    low_performing_products
)



def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # HEADER SECTION
        f.write("=" * 44 + "\n")
        f.write("          SALES ANALYTICS REPORT\n")
        f.write(f"    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"    Records Processed: {len(transactions)}\n")
        f.write("=" * 44 + "\n\n")



        # OVERALL SUMMARY
        total_revenue = sum(t['Quantity'] * t['UnitPrice'] for t in transactions)
        total_transactions = len(transactions)
        avg_order_value = total_revenue / total_transactions if total_transactions else 0

        dates = [t['Date'] for t in transactions]
        start_date = min(dates)
        end_date = max(dates)

        f.write("OVERALL SUMMARY\n")
        f.write("-" * 44 + "\n")
        f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions:   {total_transactions}\n")
        f.write(f"Average Order Value:  ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range:           {start_date} to {end_date}\n\n")


        # REGION-WISE PERFORMANCE
        region_data = region_wise_sales(transactions)

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Region':<10}{'Sales':<15}{'% of Total':<12}{'Transactions'}\n")

        for region, info in region_data.items():
            f.write(
                f"{region:<10}"
                f"₹{info['total_sales']:,.2f}  "
                f"{info['percentage']:<12}%"
                f"{info['transaction_count']}\n"
            )

        f.write("\n")


        # TOP 5 PRODUCTS
        top_products = top_selling_products(transactions, n=5)

        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Rank':<6}{'Product Name':<25}{'Qty Sold':<10}{'Revenue'}\n")

        for idx, product in enumerate(top_products, start=1):
            name, qty, revenue = product
            f.write(
                f"{idx:<6}"
                f"{name:<25}"
                f"{qty:<10}"
                f"₹{revenue:,.2f}\n"
            )

        f.write("\n")

        # TOP 5 CUSTOMERS
        customer_stats = customer_analysis(transactions)

        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Rank':<6}{'Customer ID':<15}{'Total Spent':<15}{'Orders'}\n")

        for idx, (cust_id, info) in enumerate(customer_stats.items(), start=1):
            if idx > 5:
                break

            f.write(
                f"{idx:<6}"
                f"{cust_id:<15}"
                f"₹{info['total_spent']:,.2f}  "
                f"{info['purchase_count']}\n"
            )

        f.write("\n")


        # DAILY SALES TREND
        daily_stats = daily_sales_trend(transactions)

        f.write("DAILY SALES TREND\n")
        f.write("-" * 44 + "\n")
        f.write(f"{'Date':<12}{'Revenue':<15}{'Transactions':<15}{'Unique Customers'}\n")

        for date, stats in daily_stats.items():
            f.write(
                f"{date:<12}"
                f"₹{stats['revenue']:,.2f}  "
                f"{stats['transaction_count']:<15}"
                f"{stats['unique_customers']}\n"
            )

        f.write("\n")



        # PRODUCT PERFORMANCE ANALYSIS
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 44 + "\n")

        # Best Selling Day
        best_day, best_data = max(
            daily_stats.items(),
            key=lambda x: x[1]['revenue']
        )
        f.write(
            f"Best Selling Day: {best_day} "
            f"(₹{best_data['revenue']:,.2f})\n"
        )

        # Low Performing Products
        low_products = low_performing_products(transactions)
        if low_products:
            f.write("\nLow Performing Products:\n")
            for product, qty, revenue in low_products:
                f.write(
                    f"- {product}: Qty={qty}, "
                    f"Revenue=₹{revenue:,.2f}\n"
                )
        else:
            f.write("\nLow Performing Products: None\n")

        # Average Transaction Value per Region
        f.write("\nAverage Transaction Value per Region:\n")
        for region, stats in region_data.items():
            avg_value = stats['total_sales'] / stats['transaction_count']
            f.write(f"{region}: ₹{avg_value:,.2f}\n")

        
        # =====================================================
        # 8. API ENRICHMENT SUMMARY
        # =====================================================
        
        f.write("\n\nAPI ENRICHMENT SUMMARY\n")
        f.write("-" * 44 + "\n")

        total_records = len(enriched_transactions)
        enriched_success = [t for t in enriched_transactions if t['API_Match']]
        enriched_failed = [t for t in enriched_transactions if not t['API_Match']]

        success_rate = (len(enriched_success) / total_records * 100) if total_records else 0

        f.write(f"Total Products Enriched: {len(enriched_success)}\n")
        f.write(f"Success Rate: {success_rate:.2f}%\n")

        failed_products = sorted(set(t['ProductName'] for t in enriched_failed))
        if failed_products:
            f.write("Products Not Enriched:\n")
            for product in failed_products:
                f.write(f"- {product}\n")
        else:
            f.write("Products Not Enriched: None\n")



