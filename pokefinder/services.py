import os
import time
import configparser
import numpy as np
import pandas as pd
import mysql.connector
from django.conf import settings


PATH_POKEMON_CSV = os.path.join(settings.BASE_DIR, 'pokemon.csv')
PATH_CONF = os.path.join(settings.BASE_DIR, 'conf/settings.ini')
CONFIG = configparser.ConfigParser()
CONFIG.read(PATH_CONF)
DBPARMS = CONFIG['DB']
HOST = DBPARMS['host']
DATABASE = DBPARMS['database']
USER = DBPARMS['user']
PASSWORD = DBPARMS['password']


def get_tdelta():
  tdelta = 1
  dst = time.localtime()[-1]
  if dst > 0:
    tdelta = 2
  return(tdelta)


def get_dbconnection():
  db_connection = mysql.connector.connect(
      database=DATABASE,
      host=HOST,
      user=USER,
      password=PASSWORD)
  return(db_connection)


def get_df(poke_id):
  tdelta = get_tdelta()
  query = f'select * from pokemon \
      where pokemon_id = {poke_id} \
      and latitude > 49 \
      and TIMEDIFF(NOW() - INTERVAL {tdelta} HOUR, disappear_time) < 0 \
      order by disappear_time asc;'
  cnx = get_dbconnection()
  df = pd.read_sql(query, con=cnx)
  df = df[['pokemon_id', 'latitude', 'longitude', 'disappear_time']]
  df['disappear_time'] += pd.DateOffset(hours=tdelta)
  pokedex = pd.read_csv(PATH_POKEMON_CSV)
  poke_name = pokedex[pokedex['#'] == poke_id]['Name'].iloc[0]
  df['pokemon'] = df['pokemon_id'].replace(poke_id, poke_name)
  df['disappear_time'] = df['disappear_time'].dt.strftime('%H:%M:%S')
  df = df[['pokemon', 'pokemon_id', 'disappear_time', 'latitude', 'longitude']]
  return(df)


def get_data(df):
  lst = df.values.tolist()
  cols = ['name', 'id', 'time', 'lat', 'lon']
  data = map(lambda x: dict(zip(cols, x)), lst)
  data = list(data)
  return(data)
