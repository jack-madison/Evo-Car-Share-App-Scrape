#Import the required packages
import pandas as pd
import json
import requests
from datetime import datetime
import os.path

#Contact the authentication API to get a token
oauth_url = 'https://java-us01.vulog.com/auth/realms/BCAA-CAYVR/protocol/openid-connect/token/'
data = {
    'grant_type': 'client_credentials',
    'scope': '',
    'client_id': 'BCAA-CAYVR_anon',
    'client_secret': 'dbe490f4-2f4a-4bef-8c0b-52c0ecedb6c8'
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip'
}

response = requests.post(oauth_url, data=data, headers=headers)
response = response.json()
access_token = response['access_token']
refresh_token = response['refresh_token']

#Contact the data API using the token from above to access the evo location data
data_url = 'https://java-us01.vulog.com/apiv5/availableVehicles/fc256982-77d1-455c-8ab0-7862c170db6a'

data1 = {
}

headers1 = {
    'user-lat': '49.273351',
    'user-lon': '-123.102684',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Connection': 'close',
    'Authorization': 'bearer ' + str(access_token),
    'X-API-Key': 'f52e5e56-c7db-4af0-acf5-0d8b13ac4bfc',
    'Host': 'java-us01.vulog.com',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'okhttp/3.12.8'
}

response = requests.get(data_url, data= data1, headers=headers1)
response = response.json()

#Assign the json data to a pandas dataframe
df = pd.DataFrame(response)

#Extract the data from the nested dataframes
df_status = df['status']
df_status = df_status.to_dict()
df_status = pd.DataFrame(df_status)
df_status = pd.DataFrame.transpose(df_status)

df_description = df['description']
df_description = df_description.to_dict()
df_description = pd.DataFrame(df_description)
df_description = pd.DataFrame.transpose(df_description)

df_location = df['location']
df_location = df_location.to_dict()
df_location = pd.DataFrame(df_location)
df_location = pd.DataFrame.transpose(df_location)

#Merge the extracted data back into one dataframe 
evo_data = pd.merge(df_status, df_description, left_index=True, right_index=True)
evo_data = pd.merge(evo_data, df_location, left_index=True, right_index=True)

#Split the location variable into lat and lon variables
evo_data_coor = evo_data['position']
evo_data_coor = evo_data_coor.to_dict()
evo_data_coor = pd.DataFrame(evo_data_coor)
evo_data_coor = pd.DataFrame.transpose(evo_data_coor)

evo_data = pd.merge(evo_data, evo_data_coor, left_index=True, right_index=True)

#Add a retrevied date and timestamp
evo_data['retrieved_datestamp'] = datetime.now().strftime('%Y/%m/%d')
evo_data['retrieved_timestamp'] = datetime.now().strftime('%H:%M:%S')

#Extract the variables of interest
evo_data = evo_data[['id', 'plate', 'lat', 'lon', 'energyLevel', 'retrieved_datestamp', 'retrieved_timestamp']]

#Create a new file if this is the first time that the script is run on a given day
#Otherwise append the exisiting datafile for the day
if os.path.isfile('evo_' + str(datetime.now().strftime('%Y_%m_%d')) + '.csv') == True:
    df = pd.read_csv('evo_' + str(datetime.now().strftime('%Y_%m_%d')) + '.csv')
    df = pd.DataFrame.append(df, evo_data, ignore_index= True)
    df.to_csv('evo_' + str(datetime.now().strftime('%Y_%m_%d')) + '.csv', index=False)
else:
    evo_data.to_csv('evo_' + str(datetime.now().strftime('%Y_%m_%d')) + '.csv', index=False)

print('Done!')

