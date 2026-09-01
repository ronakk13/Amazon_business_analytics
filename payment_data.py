import random
import uuid
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

OUTPUT_FILE = "payments.csv"

random.seed(42)


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
        order_id,
        order_date,
        order_status,
        total_amount
    FROM orders
    """

    orders = pd.read_sql(
        query,
        connection
    )

    connection.close()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    return orders


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

    assert orders["order_date"].notna().all(), \
        "NULL order_date found"

    assert orders["total_amount"].notna().all(), \
        "NULL total_amount found"

    assert (
        orders["total_amount"] > 0
    ).all(), \
        "Zero/negative total_amount found"

    print("Order validation passed.")

    print(
        f"Minimum order amount: "
        f"₹{orders['total_amount'].min():,.2f}"
    )

    print(
        f"Maximum order amount: "
        f"₹{orders['total_amount'].max():,.2f}"
    )


# ==========================================
# Payment Mode
# ==========================================

def generate_payment_mode():

    modes = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Wallet",
        "Net Banking",
        "Cash on Delivery"
    ]

    weights = [
        35,
        20,
        15,
        10,
        8,
        12
    ]

    return random.choices(
        modes,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Payment Status
# ==========================================

def generate_payment_status(
    order_status,
    payment_mode
):

    # Returned orders
    if order_status == "Returned":
        return "Refunded"

    # Cancelled orders
    if order_status == "Cancelled":

        return random.choices(
            [
                "Failed",
                "Refunded"
            ],
            weights=[
                80,
                20
            ],
            k=1
        )[0]

    # COD
    if payment_mode == "Cash on Delivery":

        if order_status == "Delivered":
            return "Success"

        if order_status in [
            "Processing",
            "Shipped",
            "Out for Delivery"
        ]:
            return "Pending"

        return "Failed"

    # Digital payments
    if order_status in [
        "Shipped",
        "Out for Delivery",
        "Delivered"
    ]:

        return random.choices(
            [
                "Success",
                "Failed"
            ],
            weights=[
                97,
                3
            ],
            k=1
        )[0]

    # Processing
    if order_status == "Processing":

        return random.choices(
            [
                "Success",
                "Pending",
                "Failed"
            ],
            weights=[
                85,
                10,
                5
            ],
            k=1
        )[0]

    return "Pending"


# ==========================================
# Payment Gateway
# ==========================================

def generate_payment_gateway(
    payment_mode
):

    gateway_mapping = {

        "UPI": [
            "Razorpay",
            "PayU",
            "Cashfree"
        ],

        "Credit Card": [
            "Razorpay",
            "PayU",
            "Stripe"
        ],

        "Debit Card": [
            "Razorpay",
            "PayU",
            "Stripe"
        ],

        "Wallet": [
            "Razorpay",
            "PayU"
        ],

        "Net Banking": [
            "Razorpay",
            "PayU"
        ]
    }

    if payment_mode == "Cash on Delivery":
        return None

    return random.choice(
        gateway_mapping[payment_mode]
    )


# ==========================================
# Bank
# ==========================================

def generate_bank_name(
    payment_mode
):

    banks = [
        "HDFC Bank",
        "ICICI Bank",
        "SBI",
        "Axis Bank",
        "Kotak Mahindra Bank",
        "IndusInd Bank"
    ]

    if payment_mode in [
        "Credit Card",
        "Debit Card",
        "Net Banking"
    ]:

        return random.choice(banks)

    return None


# ==========================================
# Failure Reason
# ==========================================

def generate_failure_reason():

    reasons = [
        "Insufficient funds",
        "Transaction declined",
        "Bank server unavailable",
        "Payment timeout",
        "Invalid payment details",
        "Gateway error"
    ]

    return random.choice(reasons)


# ==========================================
# Payment Time
# ==========================================

def generate_payment_time(
    order_date
):

    # Same day payment
    hour = random.randint(
        8,
        22
    )

    minute = random.randint(
        0,
        59
    )

    second = random.randint(
        0,
        59
    )

    payment_time = (
        order_date.normalize()
        + pd.Timedelta(
            hours=hour,
            minutes=minute,
            seconds=second
        )
    )

    return payment_time


# ==========================================
# Transaction ID
# ==========================================

def generate_transaction_id():

    return (
        "TXN"
        + uuid.uuid4().hex.upper()
    )


# ==========================================
# Generate Payments
# ==========================================

def generate_payments(orders):

    payments = []

    print(
        f"Generating payments for "
        f"{len(orders):,} orders..."
    )

    for _, order in orders.iterrows():

        order_id = order["order_id"]

        order_date = order["order_date"]

        order_status = order["order_status"]

        # ==================================
        # CRITICAL:
        # Payment amount comes from order
        # ==================================

        total_amount = round(
            float(order["total_amount"]),
            2
        )

        payment_mode = (
            generate_payment_mode()
        )

        payment_status = (
            generate_payment_status(
                order_status,
                payment_mode
            )
        )

        payment_time = (
            generate_payment_time(
                order_date
            )
        )

        payment_gateway = (
            generate_payment_gateway(
                payment_mode
            )
        )

        bank_name = (
            generate_bank_name(
                payment_mode
            )
        )

        failure_reason = None

        if payment_status == "Failed":

            failure_reason = (
                generate_failure_reason()
            )

        # ==================================
        # Amount Paid
        # ==================================

        if payment_status in [
            "Success",
            "Refunded"
        ]:

            amount_paid = total_amount

        else:

            amount_paid = 0.00

        transaction_id = (
            generate_transaction_id()
        )

        payments.append({

            "order_id":
                order_id,

            "payment_mode":
                payment_mode,

            "payment_status":
                payment_status,

            "payment_time":
                payment_time,

            "payment_gateway":
                payment_gateway,

            "bank_name":
                bank_name,

            "failure_reason":
                failure_reason,

            "amount_paid":
                amount_paid,

            "transaction_id":
                transaction_id
        })

    return pd.DataFrame(
        payments
    )


# ==========================================
# Validate Payments
# ==========================================

def validate_payments(
    payments,
    orders
):

    # ======================================
    # Order IDs
    # ======================================

    valid_order_ids = set(
        orders["order_id"]
    )

    assert payments[
        "order_id"
    ].isin(
        valid_order_ids
    ).all(), \
        "Invalid order_id found"

    # ======================================
    # One payment per order
    # ======================================

    assert payments[
        "order_id"
    ].is_unique, \
        "Multiple payments found for an order"

    # ======================================
    # Transaction IDs
    # ======================================

    assert payments[
        "transaction_id"
    ].is_unique, \
        "Duplicate transaction_id found"

    # ======================================
    # Payment Modes
    # ======================================

    valid_modes = {
        "UPI",
        "Credit Card",
        "Debit Card",
        "Wallet",
        "Net Banking",
        "Cash on Delivery"
    }

    assert payments[
        "payment_mode"
    ].isin(
        valid_modes
    ).all(), \
        "Invalid payment_mode found"

    # ======================================
    # Payment Status
    # ======================================

    valid_statuses = {
        "Pending",
        "Success",
        "Failed",
        "Refunded"
    }

    assert payments[
        "payment_status"
    ].isin(
        valid_statuses
    ).all(), \
        "Invalid payment_status found"

    # ======================================
    # Amount
    # ======================================

    assert (
        payments["amount_paid"] >= 0
    ).all(), \
        "Invalid amount_paid found"

    # ======================================
    # Failed payments
    # ======================================

    failed_payments = payments[
        payments["payment_status"] == "Failed"
    ]

    assert failed_payments[
        "failure_reason"
    ].notna().all(), \
        "Failed payment missing failure_reason"

    # ======================================
    # Payment Time
    # ======================================

    assert payments[
        "payment_time"
    ].notna().all(), \
        "NULL payment_time found"

    # ======================================
    # CRITICAL:
    # Successful/Refunded amount check
    # ======================================

    order_amount_map = (
        orders
        .set_index("order_id")
        ["total_amount"]
    )

    expected_amounts = (
        payments["order_id"]
        .map(order_amount_map)
    )

    paid_status = payments[
        "payment_status"
    ].isin([
        "Success",
        "Refunded"
    ])

    amount_mismatch = (
        (
            payments.loc[
                paid_status,
                "amount_paid"
            ]
            -
            expected_amounts.loc[
                paid_status
            ]
        ).abs() > 0.01
    )

    mismatch_count = int(
        amount_mismatch.sum()
    )

    print(
        f"Payment amount mismatches: "
        f"{mismatch_count:,}"
    )

    assert mismatch_count == 0, \
        "PAYMENT AMOUNT MISMATCH FOUND!"

    print(
        "Payment validation passed."
    )


# ==========================================
# Export
# ==========================================

def export_payments(payments):

    payments.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "payments.csv created successfully."
    )

    print(
        f"Total payments: "
        f"{len(payments):,}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("PAYMENTS GENERATOR")
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
    # Validate Orders
    # --------------------------------------

    print(
        "\nValidating orders..."
    )

    validate_orders(
        orders
    )

    # --------------------------------------
    # Generate
    # --------------------------------------

    print(
        "\nGenerating payments..."
    )

    payments = generate_payments(
        orders
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating payments..."
    )

    validate_payments(
        payments,
        orders
    )

    # --------------------------------------
    # Export
    # --------------------------------------

    print(
        "\nExporting payments..."
    )

    export_payments(
        payments
    )

    print(
        "\nPayment generation completed."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()