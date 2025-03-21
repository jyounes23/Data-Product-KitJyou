import sys
import json
import datetime
from dateutil import parser as date_parser
from utils.query_opensearch import query_OpenSearch
from utils.query_sql import append_docket_titles
from utils.sql import connect

def filter_dockets(dockets, filter_params=None):
    if filter_params is None:
        return dockets

    agencies = filter_params.get("agencies", [])
    date_range = filter_params.get("dateRange", {})
    docket_type = filter_params.get("docketType", "")
    
    start_date = date_parser.isoparse(date_range.get("start", "1970-01-01T00:00:00Z"))
    end_date = date_parser.isoparse(date_range.get("end", datetime.datetime.utcnow().isoformat() + "Z"))
    
    filtered = []
    for docket in dockets:
        if agencies and docket.get("agencyID", "") not in agencies:
            continue
        
        if docket_type and docket.get("docketType", "") != docket_type:
            continue

        try:
            mod_date = date_parser.isoparse(docket.get("modifyDate", "1970-01-01T00:00:00Z"))
        except Exception:
            mod_date = datetime.datetime(1970, 1, 1)
        if mod_date < start_date or mod_date > end_date:
            continue
        
        filtered.append(docket)
    
    return filtered

def query(search_term, filter_params=None):
    os_results = query_OpenSearch(search_term)
    
    dockets_json = append_docket_titles(os_results, connect())
    try:
        dockets_list = json.loads(dockets_json)
    except Exception:
        dockets_list = []
    
    filtered_list = filter_dockets(dockets_list, filter_params)
    
    return json.dumps(filtered_list, ensure_ascii=False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python query.py <search_term> [<filter_params_json>]")
        sys.exit(1)
    
    search_term = sys.argv[1]
    filter_params = None

    if len(sys.argv) >= 3:
        try:
            filter_params = json.loads(sys.argv[2])
        except Exception as e:
            print("Error parsing filter params JSON:", e)
            sys.exit(1)
    
    result = query(search_term, filter_params=filter_params)
    print(result)