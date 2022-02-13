import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from iso3166 import countries

# ONCE YOU RUN, 7 PLOTLY GRAPHS WILL OPEN UP IN YOUR BROWSER AND ONE MATPLOTLIB GRAPH WILL OPEN UP ON YOUR DESKTOP

pd.options.display.float_format = '{:,.2f}'.format

data = pd.read_csv('mission_launches.csv')
data.rename(columns={"Organisation":"Organization"}, inplace=True)


# Prints out dataframe info
def check_data():
    print(f"Amount of rows and columns: {data.shape}")
    print(f"Nan:{data.isna().values.any()}\n")
    print(f"Duplicates:{data.duplicated().values.any()}",)
    print(f"Columns Names:{data.columns}")

    # Checks active vs retired rockets
    print(data["Rocket_Status"].value_counts())

    # Check the status of the mission
    print(data["Mission_Status"].value_counts())


# Removing unnecessary columns
data.drop(["Unnamed: 0", "Unnamed: 0.1"], axis=1, inplace=True)


# Counting the total rocket launches per organization
def launches_per_organization():
    organizations = data["Organization"].value_counts()
    # Using Plotly bar chart
    launch_bar = px.bar(

        organizations,
        x=organizations.index,
        y=organizations.values,
        color=organizations.index,
        labels={"y": "Launches"}
    )
    launch_bar.update_layout(
        title="Total Launches per Organization",
        xaxis_title = "Organizations",
        yaxis_title = "Total Launches",
        legend_title = "Organizations"
    )
    launch_bar.show()
launches_per_organization()


# Cost of rocket with the amounts of rockets made
def launch_price():
    # We only want prices > 0, will change str(0) back to int later on
    clean_df = data[data["Price"] > str(0)].sort_values("Price", ascending=False)
    # Using plotly histogram
    histogram = px.histogram(
        clean_df,
        x="Price",
        color="Price",
        nbins=20,
        labels={'Price': 'Price (In Millions $)'},
        title="Amount of Rockets to Price"
    )

    histogram.show()
launch_price()


# Adding and manipulating columns
def add_columns():
    # Creating Country column
    data['Country'] = data["Location"].str.split(", ").str[-1]
    # Manipulating Country Column
    data['Country'].replace({'Gran Canaria': 'USA', 'Yellow Sea': 'China', 'Pacific Missile Range Facility': 'USA', 'Barents Sea': 'Russian Federation', 'Russia': 'Russian Federation', 'Pacific Ocean': 'USA', 'Marshall Islands': 'USA', 'Iran': 'Iran, Islamic Republic of', 'North Korea': "Korea, Democratic People's Republic of", 'South Korea': "Korea, Republic of", "Shahrud Missile Test Site": "Iran, Islamic Republic of", "New Mexico": "USA"}, inplace=True)
    # Creating ISO column
    data["ISO"] = data['Country'].apply(lambda x:(countries.get(x).alpha3))
add_columns()


# Map of total rocket launches per country
def rocket_launches_per_country():
    # Grouping Country and ISO columns with the amount of launches
    country_launches = data.groupby(["Country", "ISO"], as_index=False).agg({"Mission_Status": pd.Series.count})

    # Plotly choropleth graph
    map = px.choropleth(
        country_launches,
        locations="ISO",
        color="Mission_Status",
        color_continuous_scale='matter',
        labels={"Mission_Status": "Total Launches"},
        title="Rocket Launches per Country"
    )
    map.show()
rocket_launches_per_country()


# Map of total rocket failures per country
def failed_rocket_launches_per_country():
    # Grabbing failed launches
    launch_fail = data[data["Mission_Status"] == "Failure"].groupby(["Country", "ISO"], as_index=False).agg(
        {"Mission_Status": pd.Series.count})

    # Plotly choropleth graph
    failed_map = px.choropleth(
        launch_fail,
        locations="ISO",
        color="Mission_Status",
        color_continuous_scale='matter',
        labels={"Mission_Status": "Total Failures"},
        title="Rocket Failures per Country"

    )
    failed_map.show()
failed_rocket_launches_per_country()


# Plotly sunburst, great way to see the data
def sunburst():
    sun = px.sunburst(
        data,
        path=["Country", "Organization", 'Mission_Status'],
        title="Space Exploration Data"
    )
    sun.show()
sunburst()


# How much each organization spend in total
def amount_spent_per_organization():
    # Need to manipulate Price column to add them up
    change = [",", "nan"]
    for i in change:
        data["Price"] = data["Price"].astype(str).str.replace(i, "")

    # Changing data type
    data["Price"] = pd.to_numeric(data["Price"])

    # Grouping organizations with how much they spent on rockets
    company_spending = data.groupby("Organization", as_index=False).agg({"Price": pd.Series.sum})

    # Only want to show data of organizations that have price indicated, USSR prices are not given
    company_spending = company_spending[company_spending["Price"] > 0].sort_values("Price", ascending=False)

    print(company_spending)
amount_spent_per_organization()


# Amount of rocket launches per year
def launches_per_year():
    # Manipulating of date column
    data['Date'] = pd.to_datetime(data['Date'])

    # Creating year column
    data['year'] = data['Date'].apply(lambda x: x.year)

    # Grouping amount of launches per year
    yearly_launches = data.groupby("year", as_index=False).agg({"Mission_Status": pd.Series.count})

    # Bar chart
    launches = px.bar(
        x=yearly_launches.year,
        y=yearly_launches.Mission_Status,
        labels={"x": "Year", "y": "Launches", "color": "Launches"},
        title="Launches Per Year",
        color=yearly_launches.Mission_Status
    )
    launches.show()
launches_per_year()

# Cold war data, USA vs USSR
def cold_war():
    # Creating new df for years under 1991
    cold_war_df = data[data["year"] <= 1991]

    # Kazakhstan was part of the USSR back then, so need to manipulate data
    cold_war_df["Country"].replace({"Kazakhstan": "Russian Federation"}, inplace=True)
    cold_war_df["ISO"].replace({"KAZ": "RUS"}, inplace=True)

    # Creating another df with only USSR and USA
    ussr_vs_usa = cold_war_df[cold_war_df["Country"] == "Russian Federation"].append(
        cold_war_df[cold_war_df["Country"] == "Kazakhstan"])
    ussr_vs_usa = ussr_vs_usa.append(cold_war_df[cold_war_df["Country"] == "USA"])

    # Grouping per year launches with the countries
    yearly_super = ussr_vs_usa.groupby(["year", "Country"], as_index=False).agg({"Mission_Status": pd.Series.count})

    # Bar chart
    cold_bar = px.bar(
        yearly_super,
        x="year",
        y="Mission_Status",
        color="Country",
        barmode="group",
        labels={"year": "Year", "Mission_Status": "Launches"},
        title="USA vs USSR"
    )
    cold_bar.show()
cold_war()


def avg_price_overtime():
    # Only need prices above 0 for semi accurate data
    clean_df = data[data["Price"] > 0].sort_values("Price", ascending=False)
    # Grouping by the year and averaging the price
    avg_price_per_year = clean_df.groupby("year", as_index=False).agg({"Price": pd.Series.mean})

    # Making data look pretty
    plt.figure(figsize=(14, 8))
    plt.title("Avg Price Overtime", fontsize=14)
    plt.xticks(ticks=np.arange(1900, 2021, step=5), fontsize=14, rotation=45)
    plt.ylabel("Price in Millions $", fontsize=14)

    # Scatter plot
    plt.scatter(x=avg_price_per_year.year,
                y=avg_price_per_year.Price,
                c='dodgerblue',
                alpha=0.7,
                s=100, )

    # 3-year moving average
    moving_average = avg_price_per_year.rolling(window=3).mean()

    # Plotting the moving average on top of the scatter plot
    plt.plot(avg_price_per_year.year,
             moving_average.Price,
             c='crimson',
             linewidth=3, )

    plt.show()
avg_price_overtime()


check_data()
