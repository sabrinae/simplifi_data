import json
import requests
from datetime import date, timedelta

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
advertisers = []

for org in orgs:
  ids = org["id"]
  ads = org["name"]
  org_ids.append(str(ids))
  advertisers.append(ads)

client_merged_list = tuple(zip(org_ids,advertisers))

id_row = []
campaign_row = []
campaign_stats_row = []

yesterday_format_1 = date.strftime(date.today() - timedelta(1),"%Y-%m-%d")
print(yesterday_format_1)

i=0
while i < len(org_ids):
  campaign_url = baseUrl + org_ids[i] + "/campaigns?filter=status%3Dactive%2Cstatus%3Dpending?include=geo_fences%2Cthird_party_segments%2Cgeo_targets?attributes_only=true?size=300"
  campaign_stats_url = baseUrl + org_ids[i] + "/campaign_stats?by_campaign=true&start_date=" + yesterday_format_1 + "&end_date=" + yesterday_format_1
  i += 1
  
  campaign_response = requests.get(campaign_url, headers=params)
  campaign_data = json.loads(campaign_response.content)
  campaign_row.append(campaign_data)
  
  campaign_stats_response = requests.get(campaign_stats_url, headers=params)
  campaign_stats_data = json.loads(campaign_stats_response.content)
  campaign_stats_row.append(campaign_stats_data)

from google.colab import files #remove this when running script outside Colab
import pandas as pd

export_campaigns = []
for j in campaign_row:
  for x in j["campaigns"]:
    client_resource = x["resource"]
    print(client_resource)
    # strip all urls in client_resource variable so it only pulls the client id
    client_ids = client_resource.split("/")[5]
    campaign_name = x["name"]
    campaign_id = x["id"]
    campaign_status = x["status"]
    campaign_type = x["campaign_type"]["name"]
    start_date = x["start_date"]
    end_date = x["end_date"]
    total_NET_budget = x["total_budget"]
    
    # match back client ids in the tuple to the client ids in client_ids variable - match back appropriate client name
    for a,b in client_merged_list:
      if str(a) == str(client_ids):
        Advertiser = b
    
        export_campaigns.append([yesterday_format_1, Advertiser, client_ids, campaign_name, campaign_id, campaign_status, campaign_type, start_date, end_date, total_NET_budget])
        campaign_df = pd.DataFrame(export_campaigns)

remove_from_string = ["Daily Stats | Campaign ","|", yesterday_format_1]    
    
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
  
campaign_df.columns = ["date","Advertiser","client_id","campaign_name","campaign_id","campaign_status","campaign_type","start_date","end_date","total_NET_budget"] 
campaign_stats_df.columns = ["campaign_id","campaignstats_resource","impressions","clicks","ctr","cpm","cpc","cpa","weighted_actions","total_spend"]

yesterday_format_2 = date.strftime(date.today() - timedelta(1),"%Y%m%d")

combined_data = pd.merge_ordered(campaign_df, campaign_stats_df, on='campaign_id')
combined_data.to_csv('simplifi_' + yesterday_format_2 + '.csv')
