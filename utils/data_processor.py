# utils/data_processor.py

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    """
    transactions = []

    for line in raw_lines:
        parts = line.split('|')

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        (
            transaction_id,
            date,
            product_id,
            product_name,
            quantity,
            unit_price,
            customer_id,
            region
        ) = parts

        # Clean product name (remove commas)
        product_name = product_name.replace(',', '')

        # Clean numeric fields
        try:
            quantity = int(quantity.replace(',', ''))
            unit_price = float(unit_price.replace(',', ''))
        except ValueError:
            continue

        transactions.append({
            'TransactionID': transaction_id,
            'Date': date,
            'ProductID': product_id,
            'ProductName': product_name,
            'Quantity': quantity,
            'UnitPrice': unit_price,
            'CustomerID': customer_id,
            'Region': region
        })

    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """

    valid_transactions = []
    invalid_count = 0

    # Validation
    for t in transactions:
        if (
            t['Quantity'] <= 0 or
            t['UnitPrice'] <= 0 or
            not t['TransactionID'].startswith('T') or
            not t['ProductID'].startswith('P') or
            not t['CustomerID'].startswith('C') or
            not t['Region']
        ):
            invalid_count += 1
            continue

        valid_transactions.append(t)

    # Display available regions
    regions = sorted(set(t['Region'] for t in valid_transactions))
    print(f"Available regions: {', '.join(regions)}")

    # Display transaction amount range
    amounts = [t['Quantity'] * t['UnitPrice'] for t in valid_transactions]
    print(f"Transaction amount range: {min(amounts):.2f} - {max(amounts):.2f}")

    filtered = valid_transactions[:]
    filtered_by_region = 0
    filtered_by_amount = 0

    # Filter by region
    if region:
        filtered_by_region = sum(1 for t in filtered if t['Region'] != region)
        filtered = [t for t in filtered if t['Region'] == region]
        print(f"After region filter ({region}): {len(filtered)} records")

    # Filter by min amount
    if min_amount is not None:
        removed = [t for t in filtered if t['Quantity'] * t['UnitPrice'] < min_amount]
        filtered_by_amount += len(removed)
        filtered = [t for t in filtered if t['Quantity'] * t['UnitPrice'] >= min_amount]
        print(f"After min amount filter ({min_amount}): {len(filtered)} records")

    # Filter by max amount
    if max_amount is not None:
        removed = [t for t in filtered if t['Quantity'] * t['UnitPrice'] > max_amount]
        filtered_by_amount += len(removed)
        filtered = [t for t in filtered if t['Quantity'] * t['UnitPrice'] <= max_amount]
        print(f"After max amount filter ({max_amount}): {len(filtered)} records")

    summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered)
    }

    return filtered, invalid_count, summary


def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)
    """
    total_revenue = 0.0

    for txn in transactions:
        total_revenue += txn['Quantity'] * txn['UnitPrice']

    return round(total_revenue, 2)



def region_wise_sales(transactions):
    """
    Analyzes sales by region
    """
    region_data = {}
    total_sales_all = 0.0

    # First pass: calculate totals per region
    for txn in transactions:
        region = txn['Region']
        revenue = txn['Quantity'] * txn['UnitPrice']
        total_sales_all += revenue

        if region not in region_data:
            region_data[region] = {
                'total_sales': 0.0,
                'transaction_count': 0
            }

        region_data[region]['total_sales'] += revenue
        region_data[region]['transaction_count'] += 1

    # Second pass: calculate percentage
    for region in region_data:
        percentage = (region_data[region]['total_sales'] / total_sales_all) * 100
        region_data[region]['percentage'] = round(percentage, 2)

    # Sort by total_sales descending
    sorted_region_data = dict(
        sorted(
            region_data.items(),
            key=lambda item: item[1]['total_sales'],
            reverse=True
        )
    )

    return sorted_region_data


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    """
    product_data = {}

    # Aggregate by ProductName
    for txn in transactions:
        product = txn['ProductName']
        qty = txn['Quantity']
        revenue = txn['Quantity'] * txn['UnitPrice']

        if product not in product_data:
            product_data[product] = {'total_quantity': 0, 'total_revenue': 0.0}

        product_data[product]['total_quantity'] += qty
        product_data[product]['total_revenue'] += revenue

    # Convert to list of tuples
    product_list = [
        (product, info['total_quantity'], info['total_revenue'])
        for product, info in product_data.items()
    ]

    # Sort by total_quantity descending
    product_list.sort(key=lambda x: x[1], reverse=True)

    # Return top n products
    return product_list[:n]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    """
    customer_data = {}

    for txn in transactions:
        customer = txn['CustomerID']
        product = txn['ProductName']
        amount = txn['Quantity'] * txn['UnitPrice']

        if customer not in customer_data:
            customer_data[customer] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }

        customer_data[customer]['total_spent'] += amount
        customer_data[customer]['purchase_count'] += 1
        customer_data[customer]['products_bought'].add(product)

    # Convert products_bought from set to sorted list and calculate avg_order_value
    for customer, info in customer_data.items():
        info['products_bought'] = sorted(list(info['products_bought']))
        info['avg_order_value'] = round(info['total_spent'] / info['purchase_count'], 2)

    # Sort customers by total_spent descending
    sorted_customers = dict(
        sorted(customer_data.items(), key=lambda x: x[1]['total_spent'], reverse=True)
    )

    return sorted_customers




def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date.
    
    Returns a dictionary sorted by date:
    {
        '2024-12-01': {'revenue': 125000.0, 'transaction_count': 8, 'unique_customers': 6},
        '2024-12-02': {...},
        ...
    }
    """
    # Step 1: Initialize empty dictionary
    daily_stats = {}

    # Step 2: Loop through all transactions
    for t in transactions:
        date = t['Date']
        amount = t['Quantity'] * t['UnitPrice']
        customer = t['CustomerID']

        # Initialize date if not already in dictionary
        if date not in daily_stats:
            daily_stats[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'unique_customers': set()
            }

        # Update stats
        daily_stats[date]['revenue'] += amount
        daily_stats[date]['transaction_count'] += 1
        daily_stats[date]['unique_customers'].add(customer)

    # Step 3: Convert sets to counts
    for date, stats in daily_stats.items():
        stats['unique_customers'] = len(stats['unique_customers'])

    # Step 4: Sort dictionary by date
    sorted_daily_stats = dict(sorted(daily_stats.items(), key=lambda x: x[0]))

    return sorted_daily_stats


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)
    Example: ('2024-12-15', 185000.0, 12)
    """
    daily_stats = daily_sales_trend(transactions)

    peak_date, peak_data = max(
        daily_stats.items(),
        key=lambda item: item[1]['revenue']
    )

    return (
        peak_date,
        peak_data['revenue'],
        peak_data['transaction_count']
    )



def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low total quantity sold.

    Returns:
        list of tuples: (ProductName, TotalQuantity, TotalRevenue)
    """
    product_data = {}

    # Aggregate quantity and revenue per product
    for txn in transactions:
        product = txn['ProductName']
        qty = txn['Quantity']
        revenue = txn['Quantity'] * txn['UnitPrice']

        if product not in product_data:
            product_data[product] = {'total_quantity': 0, 'total_revenue': 0.0}

        product_data[product]['total_quantity'] += qty
        product_data[product]['total_revenue'] += revenue

    # Filter products below threshold
    low_products = [
        (product, info['total_quantity'], round(info['total_revenue'], 2))
        for product, info in product_data.items()
        if info['total_quantity'] < threshold
    ]

    # Sort by total_quantity ascending
    low_products.sort(key=lambda x: x[1])

    return low_products


