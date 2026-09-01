import random
import pandas as pd
from faker import Faker

# ==========================================
# Configuration
# ==========================================

TOTAL_SELLERS = 1000

OUTPUT_FILE = "sellers.csv"

random.seed(42)

fake = Faker("en_IN")
Faker.seed(42)


# ==========================================
# City / State
# ==========================================

CITY_STATE = {
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Bangalore": "Karnataka",
    "Hyderabad": "Telangana",
    "Pune": "Maharashtra",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Ahmedabad": "Gujarat",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh"
}


CITIES = list(CITY_STATE.keys())


# ==========================================
# Seller Types
# ==========================================

SELLER_TYPES = [
    "Brand",
    "Distributor",
    "Local"
]

SELLER_TYPE_WEIGHTS = [
    35,
    40,
    25
]


# ==========================================
# Fulfillment Types
# ==========================================

FULFILLMENT_TYPES = [
    "Amazon",
    "Seller"
]

FULFILLMENT_WEIGHTS = [
    65,
    35
]


# ==========================================
# Seller Status
# ==========================================

SELLER_STATUS = [
    "Active",
    "Inactive"
]

SELLER_STATUS_WEIGHTS = [
    92,
    8
]


# ==========================================
# Seller Name Prefix
# ==========================================

SELLER_PREFIX = [
    "Global",
    "Prime",
    "Smart",
    "Urban",
    "Elite",
    "Royal",
    "Digital",
    "Mega",
    "Tech",
    "Value"
]


# ==========================================
# Generate Sellers
# ==========================================

sellers = []

for i in range(TOTAL_SELLERS):

    # Seller type
    seller_type = random.choices(
        SELLER_TYPES,
        weights=SELLER_TYPE_WEIGHTS,
        k=1
    )[0]

    # City
    city = random.choice(CITIES)

    # State
    state = CITY_STATE[city]

    # Seller name
    seller_name = (
        f"{random.choice(SELLER_PREFIX)} "
        f"{seller_type} Store {i + 1}"
    )

    # Rating based on seller type
    if seller_type == "Brand":

        seller_rating = round(
            random.uniform(4.0, 4.9),
            1
        )

    elif seller_type == "Distributor":

        seller_rating = round(
            random.uniform(3.6, 4.7),
            1
        )

    else:

        seller_rating = round(
            random.uniform(3.0, 4.5),
            1
        )

    # Fulfillment
    fulfillment_type = random.choices(
        FULFILLMENT_TYPES,
        weights=FULFILLMENT_WEIGHTS,
        k=1
    )[0]

    # Onboarding date
    onboarding_date = fake.date_between(
        start_date="-3y",
        end_date="today"
    )

    # Seller status
    seller_status = random.choices(
        SELLER_STATUS,
        weights=SELLER_STATUS_WEIGHTS,
        k=1
    )[0]

    sellers.append({

        "seller_name": seller_name,

        "state": state,

        "city": city,

        "seller_rating": seller_rating,

        "fulfillment_type": fulfillment_type,

        "onboarding_date": onboarding_date,

        "seller_status": seller_status,

        "seller_type": seller_type
    })


# ==========================================
# DataFrame
# ==========================================

df = pd.DataFrame(sellers)


# ==========================================
# Validation
# ==========================================

assert len(df) == TOTAL_SELLERS

assert df["seller_name"].notna().all()

assert df["state"].notna().all()

assert df["city"].notna().all()

assert df["seller_rating"].between(1, 5).all()

assert df["fulfillment_type"].isin(
    FULFILLMENT_TYPES
).all()

assert df["seller_status"].isin(
    SELLER_STATUS
).all()

assert df["seller_type"].isin(
    SELLER_TYPES
).all()

assert df["onboarding_date"].notna().all()


# ==========================================
# Export
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# Summary
# ==========================================

print("Sellers generated successfully.")

print(
    f"Total sellers: {len(df):,}"
)

print("\nSeller columns:")

print(df.columns.tolist())

print("\nSeller type distribution:")

print(
    df["seller_type"]
    .value_counts()
)

print("\nFulfillment distribution:")

print(
    df["fulfillment_type"]
    .value_counts()
)

print("\nStatus distribution:")

print(
    df["seller_status"]
    .value_counts()
)

print("\nSeller data generation completed.")
