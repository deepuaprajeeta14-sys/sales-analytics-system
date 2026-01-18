import requests

def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    """
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises error for 4xx/5xx

        data = response.json()
        products = []

        for p in data.get('products', []):
            products.append({
                'id': p.get('id'),
                'title': p.get('title'),
                'category': p.get('category'),
                'brand': p.get('brand'),
                'price': p.get('price'),
                'rating': p.get('rating')
            })

        print(f"Successfully fetched {len(products)} products from API")
        return products

    except requests.exceptions.RequestException as e:
        print("Failed to fetch products from API:", e)
        return []

def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    """
    product_mapping = {}

    for product in api_products:
        product_id = product.get('id')

        if product_id is None:
            continue

        product_mapping[product_id] = {
            'title': product.get('title'),
            'category': product.get('category'),
            'brand': product.get('brand'),
            'rating': product.get('rating')
        }

    return product_mapping

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()

    Returns: list of enriched transaction dictionaries
    """
    enriched = []

    for txn in transactions:
        new_txn = txn.copy()  # Copy original transaction
        product_id_str = txn['ProductID'].lstrip('P')  # Remove 'P'
        try:
            product_id = int(product_id_str)
        except ValueError:
            product_id = None

        if product_id and product_id in product_mapping:
            api_info = product_mapping[product_id]
            new_txn['API_Category'] = api_info.get('category')
            new_txn['API_Brand'] = api_info.get('brand')
            new_txn['API_Rating'] = api_info.get('rating')
            new_txn['API_Match'] = True
        else:
            new_txn['API_Category'] = None
            new_txn['API_Brand'] = None
            new_txn['API_Rating'] = None
            new_txn['API_Match'] = False

        enriched.append(new_txn)

    return enriched

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file

    Expected File Format:
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    """
    # Define header
    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity',
        'UnitPrice', 'CustomerID', 'Region',
        'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
    ]

    with open(filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write('|'.join(header) + '\n')

        # Write each transaction
        for txn in enriched_transactions:
            row = [
                str(txn.get(col, '')) if txn.get(col) is not None else ''
                for col in header
            ]
            f.write('|'.join(row) + '\n')

    print(f"Enriched data saved to {filename}")

