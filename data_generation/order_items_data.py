import random
import numpy as np
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

OUTPUT_FILE = "order_items.csv"

random.seed(42)
np.random.seed(42)

CHUNK_SIZE = 100_000


# ==========================================
# MySQL Connection
# ==========================================

def connect_mysql():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@ronak8879340413@",
        database="amazon_business_analytics"
    )


# ==========================================
# Load Orders
# ==========================================

def load_orders():

    connection = connect_mysql()

    query = """
    SELECT
        order_id
    FROM orders
    """

    orders = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return orders


# ==========================================
# Load Products
# ==========================================

def load_products():

    connection = connect_mysql()

    query = """
    SELECT
        product_id,
        selling_price,
        stock_quantity
    FROM products
    WHERE stock_quantity > 0
    """

    products = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return products


# ==========================================
# Validate Orders
# ==========================================

def validate_orders(orders):

    assert len(orders) > 0, \
        "No orders found"

    assert orders["order_id"].is_unique, \
        "Duplicate order_id found"

    assert orders["order_id"].notna().all(), \
        "NULL order_id found"

    print("Order validation passed.")


# ==========================================
# Validate Products
# ==========================================

def validate_products(products):

    assert len(products) > 0, \
        "No products available"

    assert products["product_id"].is_unique, \
        "Duplicate product_id found"

    assert products["product_id"].notna().all(), \
        "NULL product_id found"

    assert (
        products["selling_price"] > 0
    ).all(), \
        "Invalid selling_price found"

    print("Product validation passed.")


# ==========================================
# Generate Discount
# ==========================================

def generate_discount_percentage(size):

    return np.random.choice(
        [0, 5, 10, 15, 20, 25, 30],
        size=size,
        p=[
            0.30,
            0.20,
            0.20,
            0.12,
            0.08,
            0.06,
            0.04
        ]
    )


# ==========================================
# Generate Order Items - FAST
# ==========================================

def generate_order_items(
    orders,
    products
):

    print(
        f"Generating items for "
        f"{len(orders):,} orders..."
    )

    product_ids = products[
        "product_id"
    ].to_numpy()

    product_prices = products[
        "selling_price"
    ].to_numpy()

    # --------------------------------------
    # Generate number of items per order
    # --------------------------------------

    item_counts = np.random.choice(
        [1, 2, 3, 4],
        size=len(orders),
        p=[
            0.45,
            0.30,
            0.18,
            0.07
        ]
    )

    total_items = int(
        item_counts.sum()
    )

    print(
        f"Total order items to generate: "
        f"{total_items:,}"
    )

    # --------------------------------------
    # Repeat order IDs
    # --------------------------------------

    order_ids = np.repeat(
        orders["order_id"].to_numpy(),
        item_counts
    )

    # --------------------------------------
    # Select products
    # --------------------------------------

    selected_product_indices = np.random.randint(
        0,
        len(products),
        size=total_items
    )

    selected_product_ids = (
        product_ids[
            selected_product_indices
        ]
    )

    # --------------------------------------
    # CRITICAL:
    # Price comes directly from products
    # --------------------------------------

    selling_prices = (
        product_prices[
            selected_product_indices
        ]
    )

    # --------------------------------------
    # Quantity
    # --------------------------------------

    quantities = np.random.choice(
        [1, 2, 3],
        size=total_items,
        p=[
            0.75,
            0.20,
            0.05
        ]
    )

    # --------------------------------------
    # Discount
    # --------------------------------------

    discount_percentages = (
        generate_discount_percentage(
            total_items
        )
    )

    # --------------------------------------
    # Gross amount
    # --------------------------------------

    gross_amounts = (
        selling_prices
        * quantities
    )

    # --------------------------------------
    # Discount amount
    # --------------------------------------

    discount_amounts = (
        gross_amounts
        * discount_percentages
        / 100
    )

    discount_amounts = np.round(
        discount_amounts,
        2
    )

    # --------------------------------------
    # Final price
    # --------------------------------------

    final_prices = (
        gross_amounts
        - discount_amounts
    )

    final_prices = np.round(
        final_prices,
        2
    )

    # --------------------------------------
    # Create DataFrame
    # --------------------------------------

    order_items = pd.DataFrame({

        "order_id":
            order_ids,

        "product_id":
            selected_product_ids,

        "quantity":
            quantities,

        "selling_price":
            np.round(
                selling_prices,
                2
            ),

        "discount_amount":
            discount_amounts,

        "final_price":
            final_prices
    })

    return order_items


# ==========================================
# Validate Order Items
# ==========================================

def validate_order_items(
    order_items,
    orders,
    products
):

    # --------------------------------------
    # Order IDs
    # --------------------------------------

    valid_order_ids = set(
        orders["order_id"]
    )

    assert order_items[
        "order_id"
    ].isin(
        valid_order_ids
    ).all(), \
        "Invalid order_id found"

    # --------------------------------------
    # Product IDs
    # --------------------------------------

    valid_product_ids = set(
        products["product_id"]
    )

    assert order_items[
        "product_id"
    ].isin(
        valid_product_ids
    ).all(), \
        "Invalid product_id found"

    # --------------------------------------
    # Quantity
    # --------------------------------------

    assert (
        order_items["quantity"] > 0
    ).all(), \
        "Invalid quantity found"

    # --------------------------------------
    # Selling Price
    # --------------------------------------

    assert (
        order_items["selling_price"] > 0
    ).all(), \
        "Invalid selling_price found"

    # --------------------------------------
    # Discount
    # --------------------------------------

    assert (
        order_items["discount_amount"] >= 0
    ).all(), \
        "Negative discount found"

    # --------------------------------------
    # Final Price
    # --------------------------------------

    assert (
        order_items["final_price"] > 0
    ).all(), \
        "Invalid final_price found"

    # --------------------------------------
    # Final Price Calculation
    # --------------------------------------

    expected_final_price = (
        order_items["selling_price"]
        * order_items["quantity"]
        - order_items["discount_amount"]
    )

    assert (
        (
            expected_final_price
            - order_items["final_price"]
        ).abs() < 0.01
    ).all(), \
        "Final price calculation is incorrect"

    # --------------------------------------
    # CRITICAL PRICE VALIDATION
    # --------------------------------------

    product_price_map = (
        products
        .set_index("product_id")
        ["selling_price"]
    )

    expected_product_prices = (
        order_items["product_id"]
        .map(product_price_map)
    )

    price_mismatch = (
        (
            order_items["selling_price"]
            - expected_product_prices
        ).abs() > 0.01
    )

    mismatch_count = int(
        price_mismatch.sum()
    )

    print(
        f"Product price mismatches: "
        f"{mismatch_count:,}"
    )

    assert mismatch_count == 0, \
        "PRODUCT PRICE MISMATCH FOUND!"

    print(
        "Order item validation passed."
    )


# ==========================================
# Export
# ==========================================

def export_order_items(order_items):

    order_items.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "order_items.csv created successfully."
    )

    print(
        f"Total order items: "
        f"{len(order_items):,}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("ORDER ITEMS GENERATOR")
    print("=" * 50)

    # --------------------------------------
    # Load Orders
    # --------------------------------------

    print(
        "\nLoading orders from MySQL..."
    )

    orders = load_orders()

    print(
        f"Orders loaded: "
        f"{len(orders):,}"
    )

    # --------------------------------------
    # Load Products
    # --------------------------------------

    print(
        "\nLoading products from MySQL..."
    )

    products = load_products()

    print(
        f"Products loaded: "
        f"{len(products):,}"
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating orders..."
    )

    validate_orders(
        orders
    )

    print(
        "\nValidating products..."
    )

    validate_products(
        products
    )

    # --------------------------------------
    # Generate
    # --------------------------------------

    print(
        "\nGenerating order items..."
    )

    order_items = generate_order_items(
        orders,
        products
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating order items..."
    )

    validate_order_items(
        order_items,
        orders,
        products
    )

    # --------------------------------------
    # Export
    # --------------------------------------

    print(
        "\nExporting..."
    )

    export_order_items(
        order_items
    )

    print(
        "\nOrder item generation completed."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
