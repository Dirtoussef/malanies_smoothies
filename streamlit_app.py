# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Fetching data from SmoothieFroot API (exemple initial)
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

# Establishing Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("Customize your Smoothie 🥤")

# Fetching fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Adding text input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

# User interface for selecting ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Construire ingredients_string sans espaces supplémentaires
    ingredients_string = ' '.join(ingredients_list)  # Joint les fruits avec un seul espace
    
    # Afficher les informations nutritionnelles
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")
        st.write(f'The search value for {fruit_chosen} is {search_on}')
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            smoothiefroot_response.raise_for_status()
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la récupération des données pour {fruit_chosen} : {e}")

    # Ajouter une case à cocher pour marquer la commande comme remplie
    is_filled = st.checkbox('Mark this order as FILLED', value=False)

    # Préparer une requête SQL paramétrée avec order_filled et order_ts
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled, order_ts)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP())
    """
    params = [ingredients_string, name_on_order, is_filled]

    # Bouton pour soumettre la commande
    time_to_insert = st.button('Submit Order', key='submit_order_button')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt, params).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            if is_filled:
                st.write(f"Order for {name_on_order} marked as FILLED.")
        except Exception as e:
            st.error(f"An error occurred while ordering your smoothie: {e}")
