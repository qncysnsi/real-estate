# real-estate

here are two spiders:

funda-sale-spider scrapes all properties for sale in a certain city, such as https://www.funda.nl/en/koop/1811/,
funda_sold-spider (to-do) scrapes data on properties which have (recently) been sold, such as those listed on https://www.funda.nl/en/verkocht/1811/.

# analysis
The scraped data contains the following fields: address, postal_code, price, area, rooms, bedrooms, energy certificate. For sold homes, the JSON will include posting_date and sale_date. These properties can be further analyzed using Python Pandas, for example. 

By applying geolocation to the addresses, attributes such as price per unit area can be mapped. Such attributes can be used for 'bargain hunting' by identifying outliers.

The data can also be visualized in time, and used as a gauge of market sentiment. 
