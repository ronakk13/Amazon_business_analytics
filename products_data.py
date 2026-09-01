import random
import numpy as np
import pandas as pd
import mysql.connector
from faker import Faker


# ==========================================
# Configuration
# ==========================================

TOTAL_PRODUCTS = 20000
OUTPUT_FILE = "products.csv"

random.seed(42)
np.random.seed(42)

fake = Faker("en_IN")
Faker.seed(42)


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
# Load Sellers
# ==========================================

cursor.execute("""
    SELECT seller_id, seller_type
    FROM sellers
""")

sellers = cursor.fetchall()

print(f"Sellers found: {len(sellers):,}")

assert len(sellers) > 0, "No sellers found."


# ==========================================
# Product Configuration
# ==========================================

BRAND_CATEGORIES = {

    "Samsung": [
        ("Electronics", "Smartphones"),
        ("Electronics", "Tablets"),
        ("Electronics", "TV")
    ],

    "Apple": [
        ("Electronics", "Smartphones"),
        ("Electronics", "Laptops"),
        ("Electronics", "Tablets")
    ],

    "OnePlus": [
        ("Electronics", "Smartphones"),
        ("Electronics", "Tablets")
    ],

    "Sony": [
        ("Electronics", "TV"),
        ("Electronics", "Headphones"),
        ("Electronics", "Cameras")
    ],

    "LG": [
        ("Electronics", "TV"),
        ("Electronics", "Appliances"),
        ("Electronics", "Monitors")
    ],

    "Dell": [
        ("Electronics", "Laptops"),
        ("Electronics", "Monitors")
    ],

    "HP": [
        ("Electronics", "Laptops"),
        ("Electronics", "Printers"),
        ("Electronics", "Monitors")
    ],

    "Lenovo": [
        ("Electronics", "Laptops"),
        ("Electronics", "Tablets"),
        ("Electronics", "Monitors")
    ],

    "Nike": [
        ("Fashion", "Shoes"),
        ("Fashion", "Clothing")
    ],

    "Adidas": [
        ("Fashion", "Shoes"),
        ("Fashion", "Clothing")
    ],

    "Puma": [
        ("Fashion", "Shoes"),
        ("Fashion", "Clothing")
    ],

    "Levis": [
        ("Fashion", "Jeans"),
        ("Fashion", "Clothing")
    ],

    "Boat": [
        ("Electronics", "Headphones"),
        ("Electronics", "Speakers")
    ],

    "Fastrack": [
        ("Fashion", "Watches")
    ],

    "Philips": [
        ("Home & Kitchen", "Appliances"),
        ("Electronics", "Headphones")
    ]
}


BRANDS = list(BRAND_CATEGORIES.keys())

BRAND_WEIGHTS = [
    10, 8, 7, 6, 6,
    7, 7, 6,
    8, 7, 6, 5,
    8, 4, 5
]


PRODUCT_NAMES = {

    "Samsung": [
        "Galaxy Smartphone",
        "Galaxy Tablet",
        "Smart TV"
    ],

    "Apple": [
        "iPhone",
        "MacBook",
        "iPad"
    ],

    "OnePlus": [
        "OnePlus Smartphone",
        "OnePlus Tablet"
    ],

    "Sony": [
        "Bravia TV",
        "Wireless Headphones",
        "Digital Camera"
    ],

    "LG": [
        "Smart TV",
        "Home Appliance",
        "Monitor"
    ],

    "Dell": [
        "Inspiron Laptop",
        "Business Laptop",
        "Monitor"
    ],

    "HP": [
        "Pavilion Laptop",
        "Laser Printer",
        "Monitor"
    ],

    "Lenovo": [
        "IdeaPad Laptop",
        "Tablet",
        "Monitor"
    ],

    "Nike": [
        "Running Shoes",
        "Sports T-Shirt"
    ],

    "Adidas": [
        "Running Shoes",
        "Sports T-Shirt"
    ],

    "Puma": [
        "Sports Shoes",
        "Sports T-Shirt"
    ],

    "Levis": [
        "Denim Jeans",
        "Casual Jeans"
    ],

    "Boat": [
        "Wireless Earbuds",
        "Bluetooth Speaker"
    ],

    "Fastrack": [
        "Analog Watch",
        "Smart Watch"
    ],

    "Philips": [
        "Home Appliance",
        "Wireless Headphones"
    ]
}


# ==========================================
# Generate Selling Price
# ==========================================

def generate_selling_price(category):

    if category == "Electronics":

        return round(
            random.uniform(1000, 120000),
            2
        )

    elif category == "Fashion":

        return round(
            random.uniform(500, 15000),
            2
        )

    else:

        return round(
            random.uniform(500, 30000),
            2
        )


# ==========================================
# Generate Products
# ==========================================

products = []

for i in range(TOTAL_PRODUCTS):

    # Seller
    seller_id, seller_type = random.choice(sellers)

    # Brand
    brand = random.choices(
        BRANDS,
        weights=BRAND_WEIGHTS,
        k=1
    )[0]

    # Category
    category, sub_category = random.choice(
        BRAND_CATEGORIES[brand]
    )

    # Product name
    product_name = random.choice(
        PRODUCT_NAMES[brand]
    )

    # ======================================
    # PRICE
    # ======================================

    selling_price = generate_selling_price(
        category
    )

    # Cost always LOWER than selling price
    cost_price = round(
        selling_price * random.uniform(0.60, 0.85),
        2
    )

    # ======================================
    # Stock
    # ======================================

    stock_quantity = random.randint(
        0,
        500
    )

    # ======================================
    # Product Status
    # ======================================

    if stock_quantity == 0:

        product_status = "Out of Stock"

    else:

        product_status = random.choices(
            ["Active", "Inactive"],
            weights=[95, 5],
            k=1
        )[0]

    # ======================================
    # Launch Date
    # ======================================

    launch_date = fake.date_between(
        start_date="-3y",
        end_date="today"
    )

    # ======================================
    # Weight
    # ======================================

    weight_kgs = round(
        random.uniform(0.1, 15),
        2
    )

    products.append({

        "seller_id": seller_id,

        "product_name":
            f"{brand} {product_name}",

        "brand":
            brand,

        "category":
            category,

        "sub_category":
            sub_category,

        "cost_price":
            cost_price,

        "selling_price":
            selling_price,

        "stock_quantity":
            stock_quantity,

        "product_status":
            product_status,

        "launch_date":
            launch_date,

        "weight_kgs":
            weight_kgs
    })


# ==========================================
# DataFrame
# ==========================================

df = pd.DataFrame(products)


# ==========================================
# VALIDATION
# ==========================================

assert len(df) == TOTAL_PRODUCTS

assert df["seller_id"].notna().all()

assert df["product_name"].notna().all()

assert df["brand"].notna().all()

assert df["category"].notna().all()

assert df["sub_category"].notna().all()

assert (df["cost_price"] > 0).all()

assert (df["selling_price"] > 0).all()

assert (
    df["cost_price"] < df["selling_price"]
).all()

assert (
    df["stock_quantity"] >= 0
).all()

assert (
    df["weight_kgs"] > 0
).all()

assert df["product_status"].notna().all()

assert df["launch_date"].notna().all()


# ==========================================
# FINAL PRICE VALIDATION
# ==========================================

print("\nPrice validation:")

print(
    f"Minimum cost price: "
    f"{df['cost_price'].min():,.2f}"
)

print(
    f"Maximum cost price: "
    f"{df['cost_price'].max():,.2f}"
)

print(
    f"Minimum selling price: "
    f"{df['selling_price'].min():,.2f}"
)

print(
    f"Maximum selling price: "
    f"{df['selling_price'].max():,.2f}"
)

print(
    "Cost < Selling:",
    (
        df["cost_price"]
        < df["selling_price"]
    ).all()
)


# ==========================================
# Save CSV
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# Summary
# ==========================================

print(
    "\nProducts generated successfully."
)

print(
    f"Total products: {len(df):,}"
)

print("\nCategory distribution:")

print(
    df["category"].value_counts()
)

print("\nProduct columns:")

print(
    df.columns.tolist()
)


# ==========================================
# Close MySQL
# ==========================================

cursor.close()
connection.close()

print(
    "\nMySQL connection closed."
)