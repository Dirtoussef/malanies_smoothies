# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Display the JSON response properly
try:
    st.json(smoothiefroot_response.json())
except Exception as e:
    st.error(f"An error occurred while fetching or displaying the data: {e}")

cnx = st.connection("snowflake")
session = cnx.session()
# Write directly to the app
st.title("Customize your Smoothie 🥤")

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

# User interface for selecting ingredients
ingredients_list = st.multiselect(
    'choose up 5 ingredient : ',
    options=my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"""

    st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while ordering your smoothie: {e}")
  
 
