# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Fetching data from SmoothieFroot API
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

# Establishing Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("Customize your Smoothie 🥤")

# Fetching fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Adding text input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

# User interface for selecting ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),  # Convert Snowpark DataFrame to Pandas for multiselect
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # Prepare SQL insert statement
    # Corrected the SQL string formatting to include both ingredients and name
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"""
    sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while ordering your smoothie: {e}")
 

 
