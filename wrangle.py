import pandas as pd
import numpy as np
import os
from env import get_db_url
from sklearn.model_selection import train_test_split
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
        WHERE propertylandusetypeid = 261;'''
        df_2016 = pd.read_sql(query,url)
        query = '''
        SELECT bedroomcnt,
        bathroomcnt,calculatedfinishedsquarefeet,
        taxvaluedollarcnt,yearbuilt,
        taxamount, fips 
        FROM properties_2017
        WHERE propertylandusetypeid = 261;'''
        df_2017 = pd.read_sql(query,url)
        df = pd.concat([df_2016,df_2017],axis=0)
        df.to_csv(filename,index=False)
        return df
def wrangle_zillow()->pd.DataFrame:
    #load the dataset
    df = acquire_zillow() 
    df = df.dropna()
    df.bedroomcnt = df.bedroomcnt.astype(int)
    df = df.rename(columns={'bedroomcnt':'bed_count','bathroomcnt':'bath_count',\
        'taxvaluedollarcnt':'tax_value','yearbuilt':'year_built','taxamount':'taxes',\
            'calculatedfinishedsquarefeet':'calc_finished_sqft'})
    df.year_built = df.year_built.astype(int)
    return df

def tvt_split(df:pd.DataFrame,stratify:str = None,tv_split:float = .2,validate_split:float= .3):
    '''tvt_split takes a pandas DataFrame, a string specifying the variable to stratify over,
    as well as 2 floats where 0< f < 1 and returns a train, validate, and test split of the DataFame,
    split by tv_split initially and validate_split thereafter. '''
    train_validate, test = train_test_split(df,test_size=tv_split,random_state=123,stratify=stratify)
    train, validate = train_test_split(train_validate,test_size=validate_split,random_state=123,stratify=stratify)
    return train,validate,test