import pandas as pd
from geopy.distance import geodesic

# Sample user location (latitude, longitude)
user_location = (37.7749, -122.4194)  # Example: San Francisco

# Load farmers' market dataset
# Assuming dataset has 'Latitude' & 'Longitude' columns,
# and also 'MarketName' and 'City' for the final print.
try:
    df = pd.read_excel("farmersmarket_2025-58162612.xlsx")
except FileNotFoundError:
    print("Error: 'farmersmarket_2025-58162612.xlsx' not found.")
    print("Please make sure the file exists in the same directory as the script,")
    print("or provide the full path to the file.")
    exit()
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Ensure necessary columns exist
required_columns = ["Latitude", "Longitude", "MarketName", "City"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Error: The CSV file is missing the following required columns: {', '.join(missing_columns)}")
    exit()

# Function to calculate distance
def calculate_distance(market_lat, market_lon, user_loc):
    """Calculates the geodesic distance between a market and the user."""
    market_location = (market_lat, market_lon)
    return geodesic(user_loc, market_location).km

# Apply distance calculation
# Ensure Latitude and Longitude are numeric
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

# Drop rows where conversion to numeric failed or where original values were missing
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

if not df.empty:
    df["Distance_km"] = df.apply(
        lambda row: calculate_distance(row["Latitude"], row["Longitude"], user_location),
        axis=1
    )

    # Filter by distance (e.g., markets within 20km)
    distance_threshold_km = 20
    recommended_markets = df[df["Distance_km"] <= distance_threshold_km].sort_values("Distance_km")

    # Display top 5 recommendations
    if not recommended_markets.empty:
        print(f"Top 5 farmers' markets within {distance_threshold_km}km of {user_location}:")
        print(recommended_markets[["MarketName", "City", "Distance_km"]].head())
    else:
        print(f"No farmers' markets found within {distance_threshold_km}km of {user_location}.")
else:
    print("No valid market data to process after cleaning.")