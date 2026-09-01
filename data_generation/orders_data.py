import random
import numpy as np
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

TOTAL_ORDERS = 1_000_000

START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")

random.seed(42)
np.random.seed(42)


# ==========================================
# Connect to MySQL
# ==========================================

def connect_mysql():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="@ronak8879340413@",
        database="amazon_business_analytics"
    )

    return connection


# ==========================================
# Load Customers
# ==========================================

def load_customers():

    connection = connect_mysql()

    query = """
    SELECT
        customer_id,
        signup_date,
        customer_type,
        prime_member,
        is_active
    FROM customers
    """

    customers = pd.read_sql(
        query,
        connection
    )

    connection.close()

    # Convert MySQL DATE to Pandas datetime
    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"]
    )

    return customers


# ==========================================
# Validate Customers
# ==========================================

def validate_customers(customers):

    assert customers["customer_id"].is_unique, \
        "Duplicate customer_id found"

    assert customers["customer_id"].notna().all(), \
        "NULL customer_id found"

    assert customers["signup_date"].notna().all(), \
        "NULL signup_date found"

    assert customers["customer_type"].isin(
        ["New", "Returning", "Loyal"]
    ).all(), \
        "Invalid customer_type found"

    print("Customer validation passed.")


# ==========================================
# Calculate Purchase Weights
# ==========================================

def calculate_purchase_weights(customers):

    customers = customers.copy()

    customer_type_weights = {
        "New": 0.7,
        "Returning": 1.5,
        "Loyal": 3.0
    }

    customers["purchase_weight"] = (
        customers["customer_type"]
        .map(customer_type_weights)
    )

    # Prime customers purchase more frequently

    prime_mask = (
        customers["prime_member"] == 1
    )

    customers.loc[
        prime_mask,
        "purchase_weight"
    ] *= 1.4

    # Inactive customers purchase less

    inactive_mask = (
        customers["is_active"] == 0
    )

    customers.loc[
        inactive_mask,
        "purchase_weight"
    ] *= 0.35

    return customers


# ==========================================
# Select Customers For Orders
# ==========================================

def select_customers(customers):

    # Customers who signed up during
    # or before the order period

    valid_customers = customers[
        customers["signup_date"] <= END_DATE
    ].copy()

    assert len(valid_customers) > 0, \
        "No valid customers found"

    weights = (
        valid_customers["purchase_weight"]
        .to_numpy()
    )

    weights = weights / weights.sum()

    selected_indices = np.random.choice(
        valid_customers.index,
        size=TOTAL_ORDERS,
        replace=True,
        p=weights
    )

    selected_customers = (
        valid_customers
        .loc[selected_indices]
        .reset_index(drop=True)
    )

    return selected_customers


# ==========================================
# Generate Order Date
# ==========================================

def generate_order_date(signup_date):

    start_date = max(
        signup_date,
        START_DATE
    )

    if start_date > END_DATE:
        return None

    possible_dates = pd.date_range(
        start=start_date,
        end=END_DATE,
        freq="D"
    )

    # Seasonal demand

    month_weights = {
        1: 0.85,
        2: 0.90,
        3: 0.95,
        4: 0.85,
        5: 1.00,
        6: 0.90,
        7: 1.00,
        8: 1.05,
        9: 1.00,
        10: 1.35,
        11: 1.55,
        12: 1.20
    }

    weights = np.array([
        month_weights[date.month]
        for date in possible_dates
    ])

    weights = weights / weights.sum()

    selected_date = np.random.choice(
        possible_dates,
        p=weights
    )

    return pd.Timestamp(
        selected_date
    )


# ==========================================
# Generate Order Status
# ==========================================

def generate_order_status():

    statuses = [
        "Delivered",
        "Cancelled",
        "Returned",
        "Shipped",
        "Out for Delivery",
        "Processing"
    ]

    weights = [
        80,
        6,
        5,
        4,
        3,
        2
    ]

    return random.choices(
        statuses,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Generate Orders
# ==========================================

def generate_orders(customers):

    print(
        f"Generating {TOTAL_ORDERS:,} orders..."
    )

    selected_customers = select_customers(
        customers
    )

    orders = []

    for _, customer in selected_customers.iterrows():

        customer_id = customer[
            "customer_id"
        ]

        signup_date = customer[
            "signup_date"
        ]

        # ----------------------------------
        # Order Date
        # ----------------------------------

        order_date = generate_order_date(
            signup_date
        )

        # ----------------------------------
        # Order Status
        # ----------------------------------

        order_status = generate_order_status()

        # ----------------------------------
        # Create Order
        # ----------------------------------

        orders.append({

            "customer_id":
                customer_id,

            "order_date":
                order_date,

            "order_status":
                order_status,

            # Will be calculated later
            # from order_items
            "total_amount":
                None
        })

    return pd.DataFrame(
        orders
    )


# ==========================================
# Validate Orders
# ==========================================

def validate_orders(
    orders,
    customers
):

    # --------------------------------------
    # Customer ID
    # --------------------------------------

    valid_customer_ids = set(
        customers["customer_id"]
    )

    assert orders["customer_id"].isin(
        valid_customer_ids
    ).all(), \
        "Invalid customer_id found"

    # --------------------------------------
    # Order Date
    # --------------------------------------

    assert orders["order_date"].notna().all(), \
        "NULL order_date found"

    assert (
        orders["order_date"] >= START_DATE
    ).all(), \
        "Order before START_DATE found"

    assert (
        orders["order_date"] <= END_DATE
    ).all(), \
        "Order after END_DATE found"

    # --------------------------------------
    # Signup Date Rule
    # --------------------------------------

    customer_signup = customers[
        [
            "customer_id",
            "signup_date"
        ]
    ]

    validation_df = orders.merge(
        customer_signup,
        on="customer_id",
        how="left"
    )

    assert (
        validation_df["order_date"]
        >= validation_df["signup_date"]
    ).all(), \
        "Order before customer signup found"

    # --------------------------------------
    # Order Status
    # --------------------------------------

    valid_statuses = {
        "Delivered",
        "Cancelled",
        "Returned",
        "Shipped",
        "Out for Delivery",
        "Processing"
    }

    assert orders["order_status"].isin(
        valid_statuses
    ).all(), \
        "Invalid order_status found"

    # --------------------------------------
    # Total Amount
    # --------------------------------------

    assert orders["total_amount"].isna().all(), \
        "total_amount should be NULL before order_items"

    print("Order validation passed.")


# ==========================================
# Export Orders
# ==========================================

def export_orders(orders):

    orders.to_csv(
        "orders.csv",
        index=False
    )

    print(
        "orders.csv created successfully."
    )

    print(
        f"Total orders: "
        f"{len(orders):,}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("E-COMMERCE ORDERS GENERATOR")
    print("=" * 50)

    # --------------------------------------
    # Load Customers
    # --------------------------------------

    print(
        "\nLoading customers from MySQL..."
    )

    customers = load_customers()

    print(
        f"Customers loaded: "
        f"{len(customers):,}"
    )

    # --------------------------------------
    # Validate Customers
    # --------------------------------------

    print(
        "\nValidating customers..."
    )

    validate_customers(
        customers
    )

    # --------------------------------------
    # Calculate Purchase Weights
    # --------------------------------------

    print(
        "\nCalculating purchase weights..."
    )

    customers = calculate_purchase_weights(
        customers
    )

    # --------------------------------------
    # Generate Orders
    # --------------------------------------

    print(
        "\nGenerating orders..."
    )

    orders = generate_orders(
        customers
    )

    # --------------------------------------
    # Validate Orders
    # --------------------------------------

    print(
        "\nValidating orders..."
    )

    validate_orders(
        orders,
        customers
    )

    # --------------------------------------
    # Export
    # --------------------------------------

    print(
        "\nExporting orders..."
    )

    export_orders(
        orders
    )

    print(
        "\nOrder generation completed successfully."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
