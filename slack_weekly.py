import requests
from datetime import datetime
import json

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
message = {"text": "Weekly statistics of user search queries: <http://ves-hx-a4:5601/app/kibana#/dashboard/11f73610-6891-11e7-b156-a17f885e87e7?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-7d,mode:quick,to:now))&_a=(filters:!(),options:(darkTheme:!f),panels:!((col:1,id:'943050f0-687b-11e7-b156-a17f885e87e7',panelIndex:1,row:1,size_x:6,size_y:8,type:visualization),(col:7,columns:!(_source),id:'9dc91050-687d-11e7-b156-a17f885e87e7',panelIndex:2,row:1,size_x:6,size_y:8,sort:!('@timestamp',desc),type:search)),query:(query_string:(analyze_wildcard:!t,query:'*')),timeRestore:!f,title:'Search%20queries%20(Last%207%20days)',uiState:(P-1:(vis:(params:(sort:(columnIndex:!n,direction:!n))))),viewMode:view)|Kibana dashboard>"}
requests.post("https://hooks.slack.com/services/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", json.dumps(message), headers=headers)
