import random
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

OUTPUT_FILE = "deliveries.csv"

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
        order_status
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
# Load Active Delivery Partners
# ==========================================

def load_delivery_partners():

    connection = connect_mysql()

    query = """
    SELECT
        delivery_partner_id
    FROM delivery_partners
    WHERE partner_status = 'Active'
    """

    partners = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return partners


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

    assert orders["order_status"].notna().all(), \
        "NULL order_status found"

    print(
        "Order validation passed."
    )


# ==========================================
# Validate Partners
# ==========================================

def validate_partners(partners):

    assert len(partners) > 0, \
        "No active delivery partners found"

    assert partners[
        "delivery_partner_id"
    ].is_unique, \
        "Duplicate delivery_partner_id found"

    assert partners[
        "delivery_partner_id"
    ].notna().all(), \
        "NULL delivery_partner_id found"

    print(
        "Delivery partner validation passed."
    )


# ==========================================
# Generate Delivery Status
# ==========================================

def generate_delivery_status(order_status):

    if order_status == "Cancelled":

        return "Cancelled"

    if order_status == "Returned":

        return "Delivered"

    if order_status == "Processing":

        return random.choices(
            [
                "Pending",
                "Shipped"
            ],
            weights=[
                70,
                30
            ],
            k=1
        )[0]

    if order_status == "Shipped":

        return random.choices(
            [
                "Shipped",
                "Out for Delivery",
                "Delivered"
            ],
            weights=[
                30,
                25,
                45
            ],
            k=1
        )[0]

    if order_status == "Out for Delivery":

        return random.choices(
            [
                "Out for Delivery",
                "Delivered",
                "Failed"
            ],
            weights=[
                25,
                70,
                5
            ],
            k=1
        )[0]

    if order_status == "Delivered":

        return random.choices(
            [
                "Delivered",
                "Failed"
            ],
            weights=[
                98,
                2
            ],
            k=1
        )[0]

    return "Pending"


# ==========================================
# Generate Estimated Date
# ==========================================

def generate_estimated_date(order_date):

    delivery_days = random.randint(
        2,
        7
    )

    return (
        order_date
        + pd.Timedelta(
            days=delivery_days
        )
    )


# ==========================================
# Generate Actual Delivery Date
# ==========================================

def generate_actual_delivery_date(
    estimated_date,
    delivery_status
):

    if delivery_status != "Delivered":

        return None

    delay_chance = random.random()

    if delay_chance < 0.85:

        extra_days = random.randint(
            0,
            1
        )

    else:

        extra_days = random.randint(
            2,
            4
        )

    extra_hours = random.randint(
        1,
        10
    )

    return (
        estimated_date
        + pd.Timedelta(
            days=extra_days,
            hours=extra_hours
        )
    )


# ==========================================
# Generate Service Availability
# ==========================================

def generate_service_available():

    return random.choices(
        [True, False],
        weights=[
            97,
            3
        ],
        k=1
    )[0]


# ==========================================
# Generate Delay Reason
# ==========================================

def generate_delay_reason(
    estimated_date,
    actual_date
):

    if actual_date is None:

        return None

    if actual_date <= estimated_date:

        return None

    reasons = [
        "Weather",
        "High Order Volume",
        "Partner Delay",
        "Address Issue",
        "Traffic",
        "Warehouse Delay"
    ]

    return random.choice(
        reasons
    )


# ==========================================
# Generate Deliveries
# ==========================================

def generate_deliveries(
    orders,
    partners
):

    deliveries = []

    print(
        f"Generating deliveries for "
        f"{len(orders):,} orders..."
    )

    partner_ids = partners[
        "delivery_partner_id"
    ].tolist()

    # --------------------------------------
    # Generate one delivery per order
    # --------------------------------------

    for _, order in orders.iterrows():

        order_id = order[
            "order_id"
        ]

        order_date = order[
            "order_date"
        ]

        order_status = order[
            "order_status"
        ]

        # ----------------------------------
        # Delivery Partner
        # ----------------------------------

        delivery_partner_id = random.choice(
            partner_ids
        )

        # ----------------------------------
        # Service Availability
        # ----------------------------------

        service_available = (
            generate_service_available()
        )

        # ----------------------------------
        # Delivery Status
        # ----------------------------------

        delivery_status = (
            generate_delivery_status(
                order_status
            )
        )

        # ----------------------------------
        # Service unavailable
        # ----------------------------------

        if not service_available:

            if delivery_status not in [
                "Cancelled",
                "Delivered"
            ]:

                delivery_status = "Failed"

        # ----------------------------------
        # Estimated Date
        # ----------------------------------

        estimated_date = (
            generate_estimated_date(
                order_date
            )
        )

        # ----------------------------------
        # Actual Date
        # ----------------------------------

        actual_date = (
            generate_actual_delivery_date(
                estimated_date,
                delivery_status
            )
        )

        # ----------------------------------
        # Delay Reason
        # ----------------------------------

        delay_reason = (
            generate_delay_reason(
                estimated_date,
                actual_date
            )
        )

        # ----------------------------------
        # Append
        # ----------------------------------

        deliveries.append({

            "order_id":
                order_id,

            "delivery_partner_id":
                delivery_partner_id,

            "delivery_status":
                delivery_status,

            "estimated_delivery_date":
                estimated_date,

            "actual_delivery_date":
                actual_date,

            "service_available":
                int(service_available),

            "delay_reason":
                delay_reason
        })

    return pd.DataFrame(
        deliveries
    )


# ==========================================
# Validate Deliveries
# ==========================================

def validate_deliveries(
    deliveries,
    orders,
    partners
):

    # --------------------------------------
    # One delivery per order
    # --------------------------------------

    assert deliveries[
        "order_id"
    ].is_unique, \
        "Multiple deliveries found for same order"

    # --------------------------------------
    # Valid Order IDs
    # --------------------------------------

    valid_order_ids = set(
        orders["order_id"]
    )

    assert deliveries[
        "order_id"
    ].isin(
        valid_order_ids
    ).all(), \
        "Invalid order_id found"

    # --------------------------------------
    # Valid Partner IDs
    # --------------------------------------

    valid_partner_ids = set(
        partners[
            "delivery_partner_id"
        ]
    )

    assert deliveries[
        "delivery_partner_id"
    ].isin(
        valid_partner_ids
    ).all(), \
        "Invalid delivery_partner_id found"

    # --------------------------------------
    # Delivery Status
    # --------------------------------------

    valid_statuses = {
        "Pending",
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Failed",
        "Cancelled"
    }

    assert deliveries[
        "delivery_status"
    ].isin(
        valid_statuses
    ).all(), \
        "Invalid delivery_status found"

    # --------------------------------------
    # Service Available
    # --------------------------------------

    assert deliveries[
        "service_available"
    ].isin(
        [0, 1]
    ).all(), \
        "Invalid service_available found"

    # --------------------------------------
    # Estimated Date
    # --------------------------------------

    assert deliveries[
        "estimated_delivery_date"
    ].notna().all(), \
        "NULL estimated_delivery_date found"

    # --------------------------------------
    # Actual Date
    # --------------------------------------

    delivered = deliveries[
        deliveries["delivery_status"]
        == "Delivered"
    ]

    assert delivered[
        "actual_delivery_date"
    ].notna().all(), \
        "Delivered order missing actual date"

    non_delivered = deliveries[
        deliveries["delivery_status"]
        != "Delivered"
    ]

    assert non_delivered[
        "actual_delivery_date"
    ].isna().all(), \
        "Non-delivered order has actual date"

    # --------------------------------------
    # Actual Date must be >= Estimated Date
    # --------------------------------------

    delivered = delivered.copy()

    assert (
        delivered[
            "actual_delivery_date"
        ]
        >=
        delivered[
            "estimated_delivery_date"
        ]
    ).all(), \
        "Actual delivery date before estimated date"

    # --------------------------------------
    # Delay Reason consistency
    # --------------------------------------

    delayed = deliveries[
        deliveries["actual_delivery_date"].notna()
        &
        (
            deliveries["actual_delivery_date"]
            >
            deliveries["estimated_delivery_date"]
        )
    ]

    assert delayed[
        "delay_reason"
    ].notna().all(), \
        "Delayed delivery missing delay_reason"

    print(
        "Delivery validation passed."
    )


# ==========================================
# Export
# ==========================================

def export_deliveries(
    deliveries
):

    deliveries.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "deliveries.csv created successfully."
    )

    print(
        f"Total deliveries: "
        f"{len(deliveries):,}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("DELIVERIES GENERATOR")
    print("=" * 50)

    # --------------------------------------
    # Load Orders
    # --------------------------------------

    print(
        "\nLoading orders..."
    )

    orders = load_orders()

    print(
        f"Orders loaded: "
        f"{len(orders):,}"
    )

    # --------------------------------------
    # Load Partners
    # --------------------------------------

    print(
        "\nLoading delivery partners..."
    )

    partners = load_delivery_partners()

    print(
        f"Active partners loaded: "
        f"{len(partners):,}"
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating..."
    )

    validate_orders(
        orders
    )

    validate_partners(
        partners
    )

    # --------------------------------------
    # Generate
    # --------------------------------------

    print(
        "\nGenerating deliveries..."
    )

    deliveries = generate_deliveries(
        orders,
        partners
    )

    # --------------------------------------
    # Validate
    # --------------------------------------

    print(
        "\nValidating deliveries..."
    )

    validate_deliveries(
        deliveries,
        orders,
        partners
    )

    # --------------------------------------
    # Export
    # --------------------------------------

    print(
        "\nExporting..."
    )

    export_deliveries(
        deliveries
    )

    print(
        "\nDelivery generation completed."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
