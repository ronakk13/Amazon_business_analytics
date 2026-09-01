import random
import uuid
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

OUTPUT_FILE = "returns.csv"

RETURN_RATE = 0.07

random.seed(42)


# ==========================================
# MySQL Connection
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
# Load Eligible Order Items
# ==========================================

def load_order_items():

    connection = connect_mysql()

    query = """
    SELECT
        oi.order_item_id,
        oi.final_price,
        o.order_date,
        o.order_status
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status IN (
        'Delivered',
        'Returned'
    )
    """

    order_items = pd.read_sql(
        query,
        connection
    )

    connection.close()

    order_items["order_date"] = pd.to_datetime(
        order_items["order_date"]
    )

    return order_items


# ==========================================
# Validate Order Items
# ==========================================

def validate_order_items(order_items):

    assert len(order_items) > 0, \
        "No eligible order items found"

    assert order_items[
        "order_item_id"
    ].is_unique, \
        "Duplicate order_item_id found"

    assert order_items[
        "order_item_id"
    ].notna().all(), \
        "NULL order_item_id found"

    assert (
        order_items["final_price"] > 0
    ).all(), \
        "Invalid final_price found"

    print(
        "Order item validation passed."
    )


# ==========================================
# Generate Return Reason
# ==========================================

def generate_return_reason():

    reasons = [
        "Product damaged",
        "Product defective",
        "Wrong product received",
        "Product not as expected",
        "Size or fit issue",
        "Missing parts or accessories",
        "Changed mind",
        "Quality not satisfactory"
    ]

    weights = [
        15,
        15,
        12,
        15,
        12,
        8,
        10,
        13
    ]

    return random.choices(
        reasons,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Generate Return Status
# ==========================================

def generate_return_status():

    statuses = [
        "Pending",
        "Approved",
        "Rejected"
    ]

    weights = [
        10,
        82,
        8
    ]

    return random.choices(
        statuses,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Generate Return Date
# ==========================================

def generate_return_date(order_date):

    return order_date + pd.Timedelta(
        days=random.randint(2, 30),
        hours=random.randint(1, 23),
        minutes=random.randint(0, 59)
    )


# ==========================================
# Generate Inspection Status
# ==========================================

def generate_inspection_status(
    return_status
):

    if return_status == "Pending":

        return "Pending"

    if return_status == "Approved":

        return random.choices(
            ["Passed", "Failed"],
            weights=[90, 10],
            k=1
        )[0]

    # Rejected return

    return "Failed"


# ==========================================
# Generate Warehouse Received Date
# ==========================================

def generate_warehouse_received_date(
    return_date,
    return_status
):

    if return_status == "Pending":

        return None

    return return_date + pd.Timedelta(
        days=random.randint(1, 5),
        hours=random.randint(1, 12)
    )


# ==========================================
# Generate Refund Transaction ID
# ==========================================

def generate_refund_transaction_id():

    return (
        "REF"
        + uuid.uuid4().hex.upper()
    )


# ==========================================
# Generate Returns
# ==========================================

def generate_returns(order_items):

    returns = []

    total_items = len(order_items)

    target_returns = int(
        total_items * RETURN_RATE
    )

    print(
        f"Eligible order items: "
        f"{total_items:,}"
    )

    print(
        f"Target returns: "
        f"{target_returns:,}"
    )

    # --------------------------------------
    # Select items to return
    # --------------------------------------

    selected_items = order_items.sample(
        n=target_returns,
        replace=False,
        random_state=42
    )

    for _, item in selected_items.iterrows():

        order_item_id = item[
            "order_item_id"
        ]

        final_price = float(
            item["final_price"]
        )

        order_date = item[
            "order_date"
        ]

        # ----------------------------------
        # Return reason
        # ----------------------------------

        return_reason = (
            generate_return_reason()
        )

        # ----------------------------------
        # Return status
        # ----------------------------------

        return_status = (
            generate_return_status()
        )

        # ----------------------------------
        # Return date
        # ----------------------------------

        return_date = (
            generate_return_date(
                order_date
            )
        )

        # ----------------------------------
        # Inspection
        # ----------------------------------

        inspection_status = (
            generate_inspection_status(
                return_status
            )
        )

        # ----------------------------------
        # Warehouse received date
        # ----------------------------------

        warehouse_received_date = (
            generate_warehouse_received_date(
                return_date,
                return_status
            )
        )

        # ----------------------------------
        # Refund
        # ----------------------------------

        if return_status == "Approved":

            refund_amount = final_price

        else:

            refund_amount = 0.00

        # ----------------------------------
        # Refund transaction
        # ----------------------------------

        if return_status == "Approved":

            refund_transaction_id = (
                generate_refund_transaction_id()
            )

        else:

            refund_transaction_id = None

        # ----------------------------------
        # Create return
        # ----------------------------------

        returns.append({

            "order_item_id":
                order_item_id,

            "return_reason":
                return_reason,

            "return_status":
                return_status,

            "return_date":
                return_date,

            "refund_amount":
                round(
                    refund_amount,
                    2
                ),

            "refund_transaction_id":
                refund_transaction_id,

            "inspection_status":
                inspection_status,

            "warehouse_received_date":
                warehouse_received_date
        })

    return pd.DataFrame(
        returns
    )


# ==========================================
# Validate Returns
# ==========================================

def validate_returns(
    returns,
    order_items
):

    # --------------------------------------
    # Order Item IDs
    # --------------------------------------

    valid_order_item_ids = set(
        order_items["order_item_id"]
    )

    assert returns[
        "order_item_id"
    ].isin(
        valid_order_item_ids
    ).all(), \
        "Invalid order_item_id found"

    # --------------------------------------
    # Return IDs not generated in Python
    # --------------------------------------

    assert len(returns) > 0, \
        "No returns generated"

    # --------------------------------------
    # Return Status
    # --------------------------------------

    valid_statuses = {
        "Pending",
        "Approved",
        "Rejected"
    }

    assert returns[
        "return_status"
    ].isin(
        valid_statuses
    ).all(), \
        "Invalid return_status found"

    # --------------------------------------
    # Inspection Status
    # --------------------------------------

    valid_inspection_statuses = {
        "Pending",
        "Passed",
        "Failed"
    }

    assert returns[
        "inspection_status"
    ].isin(
        valid_inspection_statuses
    ).all(), \
        "Invalid inspection_status found"

    # --------------------------------------
    # Refund Amount
    # --------------------------------------

    assert (
        returns["refund_amount"] >= 0
    ).all(), \
        "Invalid refund_amount found"

    # --------------------------------------
    # Approved returns
    # --------------------------------------

    approved = returns[
        returns["return_status"]
        == "Approved"
    ]

    assert approved[
        "refund_amount"
    ].gt(0).all(), \
        "Approved return has no refund"

    assert approved[
        "refund_transaction_id"
    ].notna().all(), \
        "Approved return missing refund transaction"

    # --------------------------------------
    # Pending / Rejected
    # --------------------------------------

    unresolved = returns[
        returns["return_status"].isin([
            "Pending",
            "Rejected"
        ])
    ]

    assert (
        unresolved["refund_amount"] == 0
    ).all(), \
        "Pending/Rejected return has refund"

    assert unresolved[
        "refund_transaction_id"
    ].isna().all(), \
        "Pending/Rejected return has refund transaction"

    # --------------------------------------
    # Return Date
    # --------------------------------------

    assert returns[
        "return_date"
    ].notna().all(), \
        "NULL return_date found"

    # --------------------------------------
    # Warehouse Date
    # --------------------------------------

    pending = returns[
        returns["return_status"]
        == "Pending"
    ]

    assert pending[
        "warehouse_received_date"
    ].isna().all(), \
        "Pending return has warehouse date"

    print(
        "Return validation passed."
    )


# ==========================================
# Export
# ==========================================

def export_returns(returns):

    returns.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "returns.csv created successfully."
    )

    print(
        f"Total returns: "
        f"{len(returns):,}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("RETURNS GENERATOR")
    print("=" * 50)

    # --------------------------------------
    # Load
    # --------------------------------------

    print(
        "\nLoading eligible order items..."
    )

    order_items = load_order_items()

    print(
        f"Order items loaded: "
        f"{len(order_items):,}"
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating..."
    )

    validate_order_items(
        order_items
    )

    # --------------------------------------
    # Generate
    # --------------------------------------

    print(
        "\nGenerating returns..."
    )

    returns = generate_returns(
        order_items
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating returns..."
    )

    validate_returns(
        returns,
        order_items
    )

    # --------------------------------------
    # Export
    # --------------------------------------

    print(
        "\nExporting..."
    )

    export_returns(
        returns
    )

    print(
        "\nReturn generation completed."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
