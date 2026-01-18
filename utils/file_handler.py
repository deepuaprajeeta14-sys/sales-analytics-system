# utils/file_handler.py

def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues
    Returns list of raw data lines (header removed)
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']

    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
    else:
        print("Error: Unable to decode file with supported encodings.")
        return []

    # Remove empty lines and strip newline characters
    lines = [line.strip() for line in lines if line.strip()]

    # Remove header
    if lines:
        lines = lines[1:]

    return lines


def write_enriched_data(filename, records):
    """
    Writes cleaned records to output file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region\n")
        for record in records:
            f.write(
                f"{record['TransactionID']}|{record['Date']}|{record['ProductID']}|"
                f"{record['ProductName']}|{record['Quantity']}|"
                f"{record['UnitPrice']}|{record['CustomerID']}|{record['Region']}\n"
            )
