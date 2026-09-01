import random
import numpy as np
import pandas as pd
from faker import Faker

TOTAL_CUSTOMERS=200000
fake=Faker("en_IN")
random.seed(42)
np.random.seed(42)

CITY_STATE={
    "Mumbai":"Maharashtra",
    "Delhi":"Delhi",
    "Bangalore":"Karnataka",
    "Hyderabad":"Telangana",
    "Pune":"Maharashtra",
    "Chennai":"Tamil Nadu",
    "Kolkata":"West Bengal",
    "Ahmedabad":"Gujarat",
    "Jaipur":"Rajasthan",
    "Lucknow":"Uttar Pradesh"
}
CITY_WEIGHTS={
    "Mumbai":18,
    "Delhi":15,
    "Bangalore":14,
    "Hyderabad":12,
    "Pune":10,
    "Chennai":9,
    "Kolkata":8,
    "Ahmedabad":7,
    "Jaipur":4,
    "Lucknow":3
}
GENDERS=[
    "Male",
    "Female",
    "Other"
]
GENDER_WEIGHTS=[
    55,
    44,
    1
]
CHANNELS=[
    "Organic",
    "Google Ads",
    "Facebook Ads",
    "Instagram Ads",
    "Referral"
]
CHANNEL_WEIGHTS=[
    35,
    25,
    15,
    10,
    15
]
CUSTOMER_TYPES=[
    "New",
    "Returning",
    "Loyal"
]
CUSTOMER_TYPE_WEIGHTS=[
    35,
    45,
    20
]

def get_city():
    c=random.choices(list(CITY_STATE.keys()),
    weights=list(CITY_WEIGHTS.values()),
    k=1)[0]
    return c,CITY_STATE[c]

def get_gender():
    return random.choices(GENDERS,weights=GENDER_WEIGHTS,k=1)[0]

def get_channel():
    return random.choices(CHANNELS,weights=CHANNEL_WEIGHTS,k=1)[0]

def get_customer_type():
    return random.choices(CUSTOMER_TYPES,weights=CUSTOMER_TYPE_WEIGHTS,k=1)[0]

def get_signup_date(t):
    if t=="New": return fake.date_between(start_date="-90d",end_date="today")
    if t=="Returning": return fake.date_between(start_date="-1y",end_date="-90d")
    return fake.date_between(start_date="-2y",end_date="-1y")

def get_prime(t):
    w=[80,20] if t=="Loyal" else ([40,60] if t=="Returning" else [10,90])
    return random.choices([True,False],weights=w,k=1)[0]

def get_active(t):
    w=[99,1] if t=="Loyal" else ([97,3] if t=="Returning" else [92,8])
    return random.choices([True,False],weights=w,k=1)[0]

def get_dob():
    return fake.date_of_birth(minimum_age=18,maximum_age=65)


customers = []
for _ in range(TOTAL_CUSTOMERS):

    city, state = get_city()
    customer_type = get_customer_type()
    signup_date = get_signup_date(customer_type)
    dob = get_dob()
    gender = get_gender()
    acquisition_channel = get_channel()
    prime_member = get_prime(customer_type)
    is_active = get_active(customer_type)
    

    customers.append({
        "signup_date": signup_date,
        "dob": dob,
        "gender": gender,
        "city": city,
        "state": state,
        "acquisition_channel": acquisition_channel,
        "customer_type": customer_type,
        "prime_member": prime_member, 
        "is_active": is_active
    })

df = pd.DataFrame(customers)

# ==========================================
# Validation
# ==========================================

assert (df["city"].map(CITY_STATE) == df["state"]).all()

assert df["prime_member"].isin([True, False]).all()

assert df["is_active"].isin([True, False]).all()


# ==========================================
# Convert Boolean to 0/1
# ==========================================

df["prime_member"] = df["prime_member"].map({
    True: 1,
    False: 0
})

df["is_active"] = df["is_active"].map({
    True: 1,
    False: 0
})


# ==========================================
# Final Validation
# ==========================================

assert df["prime_member"].isin([0, 1]).all()

assert df["is_active"].isin([0, 1]).all()


# ==========================================
# Export CSV
# ==========================================

df.to_csv(
    "customers.csv",
    index=False
)

print("customers.csv generated successfully.")
print(f"Total customers: {len(df):,}")