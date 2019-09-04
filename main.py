import json
import requests

X_USER_KEY = "<some_key>"
X_APP_KEY = "<some_app_key>"
  
baseUrl = "https://app.simpli.fi/api/organizations/"
  
params = {
  'x-app-key': X_APP_KEY,
  'x-user-key': X_USER_KEY
}
  
response = requests.get(baseUrl, headers=params)
  
if response.status_code != 200:
  print('GET /organizations/ {}'.format(response.status_code))
  
data = json.loads(response.content)

orgs = data["organizations"]
org_ids = []

for org in orgs:
  ids = org["id"]
  org_ids.append(str(ids))

campaign_row = []
campaign_stats_row = []

i=0
while i < len(org_ids):
  campaign_url = baseUrl + org_ids[i] + "/campaigns?filter=status%3Dactive%2Cstatus%3Dpending?include=geo_fences%2Cthird_party_segments%2Cgeo_targets?attributes_only=true?size=300"
  campaign_stats_url = baseUrl + org_ids[i] + "/campaign_stats?by_campaign=true"
  i += 1
  
  campaign_response = requests.get(campaign_url, headers=params)
  campaign_data = json.loads(campaign_response.content)
  campaign_row.append(campaign_data)
  
  campaign_stats_response = requests.get(campaign_stats_url, headers=params)
  campaign_stats_data = json.loads(campaign_stats_response.content)
  campaign_stats_row.append(campaign_stats_data)

from google.colab import files
import pandas as pd
from datetime import date

export_campaigns = []  
for j in campaign_row:
  for x in j["campaigns"]:
    client_resource = x["resource"]
    campaign_name = x["name"]
    campaign_id = x["id"]
    campaign_status = x["status"]
    campaign_type = x["campaign_type"]["name"]
    start_date = x["start_date"]
    end_date = x["end_date"]
    total_budget = x["total_budget"]
    
    export_campaigns.append([client_resource, campaign_name, campaign_id, campaign_status, campaign_type, start_date, end_date, total_budget])
    campaign_df = pd.DataFrame(export_campaigns)

report_date = date.today().strftime("%Y-%m-%d")
remove_from_string = ["Daily Stats | Campaign ","|",report_date]    
    
export_campaign_stats = [];
for k in campaign_stats_row:
  for y in k["campaign_stats"]:
    campaignstats_resource = y["resource"]
    title = y["name"]
    
    #remove values in array above from title variable -- leaves us with just the campaign id
    for i in remove_from_string:
      title = title.replace(i,'')
    
    int_title = int(title)
    impressions = y["impressions"]
    clicks = y["clicks"]
    ctr = y["ctr"]
    cpm = y["cpm"]
    cpc = y["cpc"]
    cpa = y["cpa"]
    weighted_actions = y["weighted_actions"]
    total_spend = y["total_spend"]
    
    export_campaign_stats.append([int_title, campaignstats_resource, impressions, clicks, ctr, cpm, cpc, cpa, weighted_actions, total_spend])
    campaign_stats_df = pd.DataFrame(export_campaign_stats)

today = date.today().strftime("%Y%m%d")
  
campaign_df.columns = ["resource","campaign_name","campaign_id","campaign_status","campaign_type","start_date","end_date","total_budget"] 
campaign_stats_df.columns = ["campaign_id","campaignstats_resource","impressions","clicks","ctr","cpm","cpc","cpa","weighted_actions","total_spend"]

combined_data = pd.merge_ordered(campaign_df, campaign_stats_df, on='campaign_id')
combined_data.to_csv('sf_data_' + today + '.csv')
