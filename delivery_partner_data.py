import random
import pandas as pd


# ==========================================
# Configuration
# ==========================================

TOTAL_PARTNERS = 100

OUTPUT_FILE = "delivery_partners.csv"

random.seed(42)


# ==========================================
# Partner Names
# ==========================================

PARTNER_NAMES = [
    "FastTrack Logistics",
    "QuickMove Delivery",
    "SwiftShip Logistics",
    "BlueDart Express",
    "EcomExpress",
    "Delhivery",
    "Shadowfax",
    "XpressBees",
    "ShipRocket",
    "RapidGo Logistics",
    "SpeedCart Delivery",
    "UrbanFleet",
    "MetroMove",
    "PrimeRoute Logistics",
    "FlashDrop",
    "CitySprint",
    "QuickRoute",
    "ExpressWay",
    "GoDeliver",
    "ParcelPro"
]


# ==========================================
# Generate Partner Name
# ==========================================

def generate_partner_name(index):

    base_name = random.choice(
        PARTNER_NAMES
    )

    return f"{base_name} {index + 1}"


# ==========================================
# Generate Rating
# ==========================================

def generate_rating():

    ratings = [
        3.0,
        3.2,
        3.4,
        3.6,
        3.8,
        4.0,
        4.2,
        4.4,
        4.6,
        4.8,
        5.0
    ]

    weights = [
        2,
        2,
        3,
        5,
        8,
        12,
        15,
        18,
        17,
        12,
        6
    ]

    return random.choices(
        ratings,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Generate Vehicle Type
# ==========================================

def generate_vehicle_type():

    vehicles = [
        "Bike",
        "Scooter",
        "Van",
        "Truck"
    ]

    weights = [
        40,
        30,
        20,
        10
    ]

    return random.choices(
        vehicles,
        weights=weights,
        k=1
    )[0]


# ==========================================
# Generate Partner Status
# ==========================================

def generate_partner_status():

    return random.choices(
        ["Active", "Inactive"],
        weights=[90, 10],
        k=1
    )[0]


# ==========================================
# Generate Delivery Partners
# ==========================================

def generate_delivery_partners():

    partners = []

    for i in range(TOTAL_PARTNERS):

        partner_name = generate_partner_name(
            i
        )

        partner_rating = generate_rating()

        vehicle_type = generate_vehicle_type()

        partner_status = generate_partner_status()

        partners.append({

            "partner_name":
                partner_name,

            "partner_rating":
                partner_rating,

            "vehicle_type":
                vehicle_type,

            "partner_status":
                partner_status
        })

    return pd.DataFrame(
        partners
    )


# ==========================================
# Validate
# ==========================================

def validate_delivery_partners(
    partners
):

    assert len(partners) == TOTAL_PARTNERS, \
        "Incorrect number of partners"

    assert partners[
        "partner_name"
    ].notna().all(), \
        "NULL partner_name found"

    assert partners[
        "partner_name"
    ].is_unique, \
        "Duplicate partner_name found"

    assert (
        partners["partner_rating"] >= 0
    ).all(), \
        "Invalid rating found"

    assert (
        partners["partner_rating"] <= 5
    ).all(), \
        "Rating above 5 found"

    assert partners[
        "vehicle_type"
    ].isin([
        "Bike",
        "Scooter",
        "Van",
        "Truck"
    ]).all(), \
        "Invalid vehicle_type found"

    assert partners[
        "partner_status"
    ].isin([
        "Active",
        "Inactive"
    ]).all(), \
        "Invalid partner_status found"

    print(
        "Delivery partner validation passed."
    )


# ==========================================
# Export
# ==========================================

def export_delivery_partners(
    partners
):

    partners.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "delivery_partners.csv "
        "created successfully."
    )

    print(
        f"Total partners: "
        f"{len(partners)}"
    )


# ==========================================
# Main
# ==========================================

def main():

    print("=" * 50)
    print("DELIVERY PARTNERS GENERATOR")
    print("=" * 50)

    # Generate

    print(
        "\nGenerating delivery partners..."
    )

    partners = generate_delivery_partners()

    # Validate

    print(
        "\nValidating..."
    )

    validate_delivery_partners(
        partners
    )

    # Export

    print(
        "\nExporting..."
    )

    export_delivery_partners(
        partners
    )

    print(
        "\nDelivery partner generation "
        "completed."
    )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()