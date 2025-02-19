# Import python packages
import streamlit as st

from snowflake.snowpark.functions import col
import requests

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

st.text(smoothiefroot_response)
cnx= st.connection("snowflake")
session = cnx.session()
# Write directly to the app
st.title("Customize your Smoothie 🥤")

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
name_on_order=st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list= st.multiselect(
    'choose up 5 ingredient : '
    ,max_selections=5
    ,my_dataframe)


if ingredients_list:
  
  ingredients_string= ''
  for fruit_chosen in ingredients_list:
      ingredients_string += fruit_chosen + ' '

  #st.write(ingredients_string)

  my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """' '""" name_on_order+ '""")"""

  #st.write(my_insert_stmt)

  #st.write(my_insert_stmt)
  time_to_insert= st.button('Submit Order')

  if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
  
 
