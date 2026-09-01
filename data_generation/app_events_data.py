import random
import numpy as np
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

TOTAL_EVENTS = 3_000_000
EVENTS_PER_FILE = 500_000

SESSIONS_PER_CHUNK = 100_000

TOTAL_PARTS = TOTAL_EVENTS // EVENTS_PER_FILE

random.seed(42)
np.random.seed(42)


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
# Load Data
# ==========================================

def load_data():

    connection = connect_mysql()

    customers = pd.read_sql(
        """
        SELECT customer_id
        FROM customers
        WHERE is_active = 1
        """,
        connection
    )

    devices = pd.read_sql(
        """
        SELECT
            device_id,
            customer_id,
            brand,
            os_version
        FROM devices
        """,
        connection
    )

    products = pd.read_sql(
        """
        SELECT product_id
        FROM products
        """,
        connection
    )

    connection.close()

    return customers, devices, products


# ==========================================
# Timestamp
# ==========================================

def generate_timestamps(n):

    start = pd.Timestamp(
        "2024-01-01"
    )

    end = pd.Timestamp(
        "2025-12-31 23:59:59"
    )

    total_seconds = int(
        (end - start).total_seconds()
    )

    seconds = np.random.randint(
        0,
        total_seconds,
        n
    )

    return (
        start
        + pd.to_timedelta(
            seconds,
            unit="s"
        )
    )


# ==========================================
# Normal Page Load Time
# ==========================================

def generate_page_load_time(n):

    return np.random.normal(
        1800,
        500,
        n
    ).clip(
        300
    ).astype(int)


# ==========================================
# Bug Page Load Time
# ==========================================

def generate_bug_page_load_time(n):

    return np.random.normal(
        5200,
        900,
        n
    ).clip(
        2500
    ).astype(int)


# ==========================================
# Create Event DataFrame
# ==========================================

def create_event(
    customer_ids,
    session_ids,
    event_name,
    event_timestamp,
    product_ids,
    device_ids,
    event_status,
    page_load_time
):

    return pd.DataFrame({

        "customer_id":
            customer_ids,

        "session_id":
            session_ids,

        "event_name":
            event_name,

        "event_timestamp":
            event_timestamp,

        "product_id":
            product_ids,

        "device_id":
            device_ids,

        "event_status":
            event_status,

        "page_load_time_ms":
            page_load_time
    })


# ==========================================
# Generate One Session Chunk
# ==========================================

def generate_chunk(
    customers,
    devices,
    products,
    session_start_number
):

    n = SESSIONS_PER_CHUNK

    # ======================================
    # CUSTOMER
    # ======================================

    customer_ids = np.random.choice(
        customers["customer_id"].values,
        size=n
    )

    # ======================================
    # SESSION
    # ======================================

    session_numbers = np.arange(
        session_start_number,
        session_start_number + n
    )

    session_ids = np.array([
        f"SES{x:010d}"
        for x in session_numbers
    ])

    # ======================================
    # DEVICE
    # ======================================

    device_lookup = (
        devices
        .set_index("customer_id")
    )

    selected_devices = (
        device_lookup
        .loc[customer_ids]
        .reset_index()
    )

    device_ids = selected_devices[
        "device_id"
    ].values

    brands = selected_devices[
        "brand"
    ].values

    os_versions = selected_devices[
        "os_version"
    ].values

    # ======================================
    # SESSION TIME
    # ======================================

    session_time = generate_timestamps(n)

    # ======================================
    # PRODUCT
    # ======================================

    product_ids = np.random.choice(
        products["product_id"].values,
        size=n
    )

    events = []

    # ======================================
    # APP OPEN
    # ======================================

    events.append(
        create_event(
            customer_ids,
            session_ids,
            "app_open",
            session_time,
            np.full(n, np.nan),
            device_ids,
            np.full(n, "Success"),
            generate_page_load_time(n)
        )
    )

    # ======================================
    # VIEW HOME
    # ======================================

    home_time = (
        session_time
        + pd.to_timedelta(
            np.random.randint(
                2,
                10,
                n
            ),
            unit="s"
        )
    )

    events.append(
        create_event(
            customer_ids,
            session_ids,
            "view_home",
            home_time,
            np.full(n, np.nan),
            device_ids,
            np.full(n, "Success"),
            generate_page_load_time(n)
        )
    )

    # ======================================
    # SEARCH
    # ======================================

    search_mask = (
        np.random.random(n)
        < 0.55
    )

    search_count = search_mask.sum()

    if search_count > 0:

        search_time = (
            home_time[search_mask]
            + pd.to_timedelta(
                np.random.randint(
                    2,
                    8,
                    search_count
                ),
                unit="s"
            )
        )

        events.append(
            create_event(
                customer_ids[search_mask],
                session_ids[search_mask],
                "search",
                search_time,
                np.full(
                    search_count,
                    np.nan
                ),
                device_ids[search_mask],
                np.full(
                    search_count,
                    "Success"
                ),
                generate_page_load_time(
                    search_count
                )
            )
        )

    # ======================================
    # PRODUCT VIEW
    # ======================================

    product_time = (
        home_time
        + pd.to_timedelta(
            np.random.randint(
                3,
                15,
                n
            ),
            unit="s"
        )
    )

    # ======================================
    # BUSINESS BUG
    #
    # Samsung + Android 14
    # March 2025
    # ======================================

    samsung_android14 = (
        (brands == "Samsung")
        &
        (os_versions == "Android 14")
    )

    bug_segment = (
        samsung_android14
        &
        (product_time.year == 2025)
        &
        (product_time.month == 3)
    )

    # ======================================
    # PRODUCT PAGE LOAD
    # ======================================

    product_load_time = (
        generate_page_load_time(n)
    )

    bug_count = bug_segment.sum()

    if bug_count > 0:

        product_load_time[
            bug_segment
        ] = generate_bug_page_load_time(
            bug_count
        )

    # ======================================
    # PRODUCT VIEW FAILURE
    # ======================================

    product_status = np.full(
        n,
        "Success",
        dtype=object
    )

    bug_view_failure = (
        bug_segment
        &
        (
            np.random.random(n)
            < 0.04
        )
    )

    product_status[
        bug_view_failure
    ] = "Failed"

    events.append(
        create_event(
            customer_ids,
            session_ids,
            "view_product",
            product_time,
            product_ids,
            device_ids,
            product_status,
            product_load_time
        )
    )

    # ======================================
    # ATC PROBABILITY
    # ======================================

    atc_probability = np.full(
        n,
        0.19
    )

    # Normal Samsung Android 14

    atc_probability[
        samsung_android14
    ] = 0.18

    # ======================================
    # BUSINESS BUG
    #
    # March 2025
    #
    # ATC:
    # 18% -> 8%
    # ======================================

    atc_probability[
        bug_segment
    ] = 0.08

    # ======================================
    # ATC DECISION
    # ======================================

    atc_mask = (
        np.random.random(n)
        < atc_probability
    )

    atc_count = atc_mask.sum()

    if atc_count > 0:

        atc_time = (
            product_time[atc_mask]
            + pd.to_timedelta(
                np.random.randint(
                    3,
                    15,
                    atc_count
                ),
                unit="s"
            )
        )

        atc_customers = (
            customer_ids[atc_mask]
        )

        atc_sessions = (
            session_ids[atc_mask]
        )

        atc_products = (
            product_ids[atc_mask]
        )

        atc_devices = (
            device_ids[atc_mask]
        )

        # ==================================
        # ATC FAILURE
        # ==================================

        atc_bug_segment = (
            bug_segment[atc_mask]
        )

        atc_failure_probability = (
            np.full(
                atc_count,
                0.02
            )
        )

        atc_failure_probability[
            atc_bug_segment
        ] = 0.25

        atc_status = np.full(
            atc_count,
            "Success",
            dtype=object
        )

        atc_failed_mask = (
            np.random.random(atc_count)
            <
            atc_failure_probability
        )

        atc_status[
            atc_failed_mask
        ] = "Failed"

        events.append(
            create_event(
                atc_customers,
                atc_sessions,
                "add_to_cart",
                atc_time,
                atc_products,
                atc_devices,
                atc_status,
                generate_page_load_time(
                    atc_count
                )
            )
        )

        # ==================================
        # SUCCESSFUL ATC ONLY
        # ==================================

        successful_atc_mask = (
            ~atc_failed_mask
        )

        successful_count = (
            successful_atc_mask.sum()
        )

        if successful_count > 0:

            cart_customers = (
                atc_customers[
                    successful_atc_mask
                ]
            )

            cart_sessions = (
                atc_sessions[
                    successful_atc_mask
                ]
            )

            cart_products = (
                atc_products[
                    successful_atc_mask
                ]
            )

            cart_devices = (
                atc_devices[
                    successful_atc_mask
                ]
            )

            successful_atc_time = (
                atc_time[
                    successful_atc_mask
                ]
            )

            # ==================================
            # VIEW CART
            # ==================================

            cart_mask = (
                np.random.random(
                    successful_count
                )
                < 0.80
            )

            cart_count = cart_mask.sum()

            if cart_count > 0:

                cart_time = (
                    successful_atc_time[
                        cart_mask
                    ]
                    + pd.to_timedelta(
                        np.random.randint(
                            3,
                            15,
                            cart_count
                        ),
                        unit="s"
                    )
                )

                cart_customers = (
                    cart_customers[
                        cart_mask
                    ]
                )

                cart_sessions = (
                    cart_sessions[
                        cart_mask
                    ]
                )

                cart_products = (
                    cart_products[
                        cart_mask
                    ]
                )

                cart_devices = (
                    cart_devices[
                        cart_mask
                    ]
                )

                events.append(
                    create_event(
                        cart_customers,
                        cart_sessions,
                        "view_cart",
                        cart_time,
                        cart_products,
                        cart_devices,
                        np.full(
                            cart_count,
                            "Success"
                        ),
                        generate_page_load_time(
                            cart_count
                        )
                    )
                )

                # ==================================
                # CHECKOUT
                # ==================================

                checkout_mask = (
                    np.random.random(
                        cart_count
                    )
                    < 0.70
                )

                checkout_count = (
                    checkout_mask.sum()
                )

                if checkout_count > 0:

                    checkout_time = (
                        cart_time[
                            checkout_mask
                        ]
                        + pd.to_timedelta(
                            np.random.randint(
                                3,
                                20,
                                checkout_count
                            ),
                            unit="s"
                        )
                    )

                    checkout_customers = (
                        cart_customers[
                            checkout_mask
                        ]
                    )

                    checkout_sessions = (
                        cart_sessions[
                            checkout_mask
                        ]
                    )

                    checkout_products = (
                        cart_products[
                            checkout_mask
                        ]
                    )

                    checkout_devices = (
                        cart_devices[
                            checkout_mask
                        ]
                    )

                    events.append(
                        create_event(
                            checkout_customers,
                            checkout_sessions,
                            "checkout",
                            checkout_time,
                            checkout_products,
                            checkout_devices,
                            np.full(
                                checkout_count,
                                "Success"
                            ),
                            generate_page_load_time(
                                checkout_count
                            )
                        )
                    )

                    # ==================================
                    # PURCHASE
                    # ==================================

                    purchase_mask = (
                        np.random.random(
                            checkout_count
                        )
                        < 0.35
                    )

                    purchase_count = (
                        purchase_mask.sum()
                    )

                    if purchase_count > 0:

                        purchase_time = (
                            checkout_time[
                                purchase_mask
                            ]
                            + pd.to_timedelta(
                                np.random.randint(
                                    5,
                                    30,
                                    purchase_count
                                ),
                                unit="s"
                            )
                        )

                        events.append(
                            create_event(
                                checkout_customers[
                                    purchase_mask
                                ],
                                checkout_sessions[
                                    purchase_mask
                                ],
                                "purchase",
                                purchase_time,
                                checkout_products[
                                    purchase_mask
                                ],
                                checkout_devices[
                                    purchase_mask
                                ],
                                np.full(
                                    purchase_count,
                                    "Success"
                                ),
                                generate_page_load_time(
                                    purchase_count
                                )
                            )
                        )

    return pd.concat(
        events,
        ignore_index=True
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 60)
    print("APP EVENTS GENERATOR")
    print("=" * 60)

    print(
        f"\nTotal events required: "
        f"{TOTAL_EVENTS:,}"
    )

    print(
        f"Events per file: "
        f"{EVENTS_PER_FILE:,}"
    )

    print(
        f"Total files: "
        f"{TOTAL_PARTS}"
    )

    # ======================================
    # Load
    # ======================================

    customers, devices, products = (
        load_data()
    )

    print(
        f"\nCustomers: {len(customers):,}"
    )

    print(
        f"Devices: {len(devices):,}"
    )

    print(
        f"Products: {len(products):,}"
    )

    # ======================================
    # Safety Checks
    # ======================================

    if len(customers) == 0:
        print(
            "ERROR: No active customers found."
        )
        return

    if len(devices) == 0:
        print(
            "ERROR: No devices found."
        )
        return

    if len(products) == 0:
        print(
            "ERROR: No products found."
        )
        return

    customer_ids = set(
        customers["customer_id"]
    )

    device_customer_ids = set(
        devices["customer_id"]
    )

    missing_devices = (
        customer_ids
        - device_customer_ids
    )

    if len(missing_devices) > 0:

        print(
            f"ERROR: "
            f"{len(missing_devices):,} "
            "customers have no device."
        )

        return

    # ======================================
    # Generate Parts
    # ======================================

    total_generated = 0
    session_number = 1

    for part_number in range(
        1,
        TOTAL_PARTS + 1
    ):

        print(
            "\n" + "=" * 60
        )

        print(
            f"GENERATING PART "
            f"{part_number}/{TOTAL_PARTS}"
        )

        print(
            "=" * 60
        )

        part_events = []

        part_count = 0

        while part_count < EVENTS_PER_FILE:

            chunk = generate_chunk(
                customers,
                devices,
                products,
                session_number
            )

            session_number += (
                SESSIONS_PER_CHUNK
            )

            remaining = (
                EVENTS_PER_FILE
                - part_count
            )

            chunk = chunk.iloc[
                :remaining
            ]

            part_events.append(
                chunk
            )

            part_count += len(chunk)

            del chunk

            print(
                f"Part progress: "
                f"{part_count:,} / "
                f"{EVENTS_PER_FILE:,}"
            )

        part_df = pd.concat(
            part_events,
            ignore_index=True
        )

        filename = (
            f"app_events_part_"
            f"{part_number}.csv"
        )

        part_df.to_csv(
            filename,
            index=False
        )

        total_generated += len(
            part_df
        )

        print(
            f"\nCreated: {filename}"
        )

        print(
            f"Rows: {len(part_df):,}"
        )

        del part_df
        del part_events

    # ======================================
    # Final
    # ======================================

    print(
        "\n" + "=" * 60
    )

    print(
        "APP EVENTS GENERATION COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Total events generated: "
        f"{total_generated:,}"
    )

    print(
        f"Total files generated: "
        f"{TOTAL_PARTS}"
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
