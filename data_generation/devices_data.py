import random
import numpy as np
import pandas as pd
import mysql.connector


# ==========================================
# Configuration
# ==========================================

OUTPUT_FILE = "devices.csv"

random.seed(42)
np.random.seed(42)


# ==========================================
# MySQL Connection
# ==========================================

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@ronak8879340413@",
    database="amazon_business_analytics"
)

cursor = connection.cursor()


# ==========================================
# Get Customers
# ==========================================

cursor.execute("""
    SELECT customer_id
    FROM customers
""")

customer_ids = [
    row[0]
    for row in cursor.fetchall()
]

print(
    f"Customers found: {len(customer_ids):,}"
)


# ==========================================
# Device Configuration
# ==========================================

BRANDS = [
    "Samsung",
    "Apple",
    "OnePlus",
    "Xiaomi",
    "Vivo",
    "Oppo",
    "Realme"
]

BRAND_WEIGHTS = [
    30,
    20,
    15,
    12,
    10,
    8,
    5
]


SAMSUNG_MODELS = [
    "A55",
    "S24",
    "A35",
    "S23",
    "M34"
]

APPLE_MODELS = [
    "iPhone 15",
    "iPhone 14",
    "iPhone 13"
]

ONEPLUS_MODELS = [
    "12R",
    "Nord 4",
    "11R"
]

XIAOMI_MODELS = [
    "Redmi Note 13",
    "14 C",
    "Poco X6"
]

VIVO_MODELS = [
    "V30",
    "V29",
    "Y200"
]

OPPO_MODELS = [
    "Reno 11",
    "A79",
    "F25"
]

REALME_MODELS = [
    "12 Pro",
    "11 Pro",
    "Narzo 70"
]


# ==========================================
# Generate Device
# ==========================================

def generate_device():

    brand = random.choices(
        BRANDS,
        weights=BRAND_WEIGHTS,
        k=1
    )[0]


    # --------------------------------------
    # Samsung
    # --------------------------------------

    if brand == "Samsung":

        model = random.choice(
            SAMSUNG_MODELS
        )

        os_version = random.choices(
            [
                "Android 13",
                "Android 14",
                "Android 15"
            ],
            weights=[
                25,
                60,
                15
            ],
            k=1
        )[0]


    # --------------------------------------
    # Apple
    # --------------------------------------

    elif brand == "Apple":

        model = random.choice(
            APPLE_MODELS
        )

        os_version = random.choices(
            [
                "iOS 17",
                "iOS 18"
            ],
            weights=[
                35,
                65
            ],
            k=1
        )[0]


    # --------------------------------------
    # Other Android brands
    # --------------------------------------

    else:

        model_map = {
            "OnePlus": ONEPLUS_MODELS,
            "Xiaomi": XIAOMI_MODELS,
            "Vivo": VIVO_MODELS,
            "Oppo": OPPO_MODELS,
            "Realme": REALME_MODELS
        }

        model = random.choice(
            model_map[brand]
        )

        os_version = random.choices(
            [
                "Android 13",
                "Android 14",
                "Android 15"
            ],
            weights=[
                25,
                60,
                15
            ],
            k=1
        )[0]


    # --------------------------------------
    # App Version
    # --------------------------------------

    app_version = random.choice(
        [
            "5.0",
            "5.1",
            "5.2",
            "5.3"
        ]
    )


    return (
        brand,
        model,
        os_version,
        app_version
    )


# ==========================================
# Generate Devices
# ==========================================

devices = []

for customer_id in customer_ids:

    brand, model, os_version, app_version = (
        generate_device()
    )

    devices.append({

        "customer_id":
            customer_id,

        "brand":
            brand,

        "model":
            model,

        "os_version":
            os_version,

        "app_version":
            app_version
    })


# ==========================================
# DataFrame
# ==========================================

df = pd.DataFrame(
    devices
)


# ==========================================
# Validation
# ==========================================

assert len(df) == len(customer_ids)

assert df[
    "customer_id"
].is_unique

assert df[
    "brand"
].notna().all()

assert df[
    "model"
].notna().all()

assert df[
    "os_version"
].notna().all()

assert df[
    "app_version"
].notna().all()


# ==========================================
# Check Samsung Android 14
# ==========================================

bug_population = df[
    (df["brand"] == "Samsung")
    &
    (df["os_version"] == "Android 14")
]

print(
    "\nSamsung Android 14 devices:",
    f"{len(bug_population):,}"
)


# ==========================================
# Save CSV
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nDevices CSV generated: "
    f"{len(df):,} rows"
)


# ==========================================
# Close MySQL
# ==========================================

cursor.close()
connection.close()

print(
    "\nDone."
)
