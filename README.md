Amazon E-commerce Business Analytics

An end-to-end E-commerce Business Analytics project built using Python, MySQL, SQL, and Power BI. The project covers the complete analytics workflow — from synthetic data generation and relational database design to business analysis, problem identification, dashboard development, and actionable recommendations.

Project Objective

The objective was to analyze an e-commerce business across different areas and identify business performance trends, revenue leakage, customer behavior, operational inefficiencies, product performance, and potential application issues.

The project follows:

Data Generation → Database Design → SQL Analysis → Problem Identification → Power BI Dashboard → Business Recommendations

Tech Stack
Python — Synthetic data generation
MySQL — Database and data storage
SQL — Data analysis and business problem identification
Power BI — Interactive dashboard and visualization
DAX — Business metrics and KPIs
Database Schema

The database contains the following major tables:

customers
products
sellers
orders
order_items
payments
deliveries
delivery_partners
returns
app_events
devices

The tables were connected using relational keys to enable analysis across customers, orders, products, operations and application events.

Data Generation

A large-scale synthetic e-commerce dataset was generated using Python with libraries such as Pandas, NumPy and Random.

The generated data represents:

Customer information
Product and seller information
Orders and order items
Payments
Deliveries
Returns
Customer acquisition
App events
Devices and app versions

Raw generated data is not included in this repository due to dataset size. The Python scripts used to generate the data are included.

SQL Analysis

SQL was used to perform exploratory and business analysis across multiple dimensions.

Sales & Profitability
Revenue
Profit
Profit Margin
AOV
Total Orders
Monthly Growth
Category performance
Customer Analysis
Unique Customers
Repeat Customers
Repeat Customer Rate
Revenue per Customer
Customer Type
Acquisition Channel
Top Customers
Product Analysis
Revenue by Category
Revenue by Sub-category
Profit by Category
Product-level performance
Return Rate by Category
Geographic & Operations
Revenue by State
Revenue by City
Order Status
Delivery Performance
Delivery Partner Analysis
Returns
Return Rate
Return Reasons
Returned Products
Return Revenue Loss
Monthly Return Trends
Category/Product Return Analysis
Payments
Payment Methods
Successful vs Failed Payments
Payment Success Rate
Refund Analysis
Funnel Analysis

Customer journey was analyzed using the app-event data:

Product View → Add to Cart → Checkout → Purchase

Since the app_events table did not contain order_id, distinct session_id was used to measure sessions reaching each funnel stage.

Event success and failure rates were analyzed separately to identify potential points of funnel leakage.

Further segmentation was performed by:

Month → Device Brand → App Version → Device Model → OS Version

This revealed an unusual Add-to-Cart failure pattern during March, particularly around:

Samsung + App Version 5.1 + Android 14

This was treated as a potential technical issue requiring investigation, not as a confirmed root cause, since detailed API/error-log data was not available.

Key Findings
Business Performance
Revenue: $92.45B
Profit: $18.80B
Profit Margin: 20.34%
Monthly Growth: 32.30%
Returns & Revenue Leakage
Returned Products: 78K
Overall Return Rate: 8.20%
Return Revenue Loss: $4.02B
Electronics Return Rate: 5.54%

Electronics had the highest return rate among the major categories, with product damage and defects being important return reasons.

Customer Analysis
Unique Customers: 86.23K
Repeat Customer Rate: 99.29%

The repeat customer rate appeared exceptionally high, so the metric was flagged for validation rather than being treated blindly as a business advantage.

Power BI Dashboard

The final Power BI dashboard contains multiple analytical pages:

Executive Overview
Customer Analysis
Geographic & Operations Analysis
Product & Category Analysis
Funnel & App Performance Analysis
Return Analysis
Payment Analysis
Business Insights & Recommendations

The dashboard converts the SQL findings into interactive KPIs, charts, trends, funnel analysis and business recommendations.

Business Recommendations

Based on the analysis:

Reduce Electronics return rates
Investigate damage and defect-related returns
Identify high-return products and sellers
Investigate the Samsung + App 5.1 + Android 14 Add-to-Cart failure pattern
Validate the unusually high repeat customer rate
Optimize inventory and operations around major revenue-contributing markets
