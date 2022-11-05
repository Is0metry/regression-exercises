import pandas as pd
import numpy as np
import os
from env import get_db_url
def clean_data_path(filename:str)->str:
    '''clean_data_path takes a string with the name of a file and modifies it to fit the desired filepath format i.e. data/*.csv'''
    if not filename.startswith('data/'):
        filename = 'data/' + filename
    if not filename.endswith('.csv'):
        filename = filename + '.csv'
    return filename
def acquire_zillow():
    filename = clean_data_path('zillow')
    if os.path.isfile(filename):
        return pd.read_csv(filename)
    else:
        url = get_db_url('zillow')
        query = '''
        SELECT bedroomcnt,
        bathroomcnt,calculatedfinishedsquarefeet,
        taxvaluedollarcnt,yearbuilt,
        taxamount, fips 
        FROM properties_2016 
        JOIN propertylandusetype
        USING(propertylandusetypeid)
        WHERE propertylandusedesc = "Single Family Residential";'''
        df_2016 = pd.read_sql(query,url)
        query = '''
        SELECT bedroomcnt,
        bathroomcnt,calculatedfinishedsquarefeet,
        taxvaluedollarcnt,yearbuilt,
        taxamount, fips 
        FROM properties_2017
        JOIN propertylandusetype
        USING(propertylandusetypeid)
        WHERE propertylandusedesc = "Single Family Residential";'''
        df_2017 = pd.read_sql(query,url)
        df = pd.concat([df_2016,df_2017],axis=0)
        df.to_csv(filename,index=False)
        return df
def wrangle_zillow()->pd.DataFrame:
    #load the dataset
    df = acquire_zillow()
    #fillna with yearbuilt (easily ignored if po)    
    df.yearbuilt = df.yearbuilt.fillna(0).astype(int)
    df = df.dropna()
    df.bedroomcnt = df.bedroomcnt.astype(int)
    df = df.rename(columns={'bedroomcnt':'bed_count','bathroomcnt':'bath_count',\
        'taxvaluedollarcnt':'tax_value','yearbuilt':'year_built','taxamount':'taxes',\
            'calculatedfinishedsquarefeet':'calc_finished_sqft'})
    return df