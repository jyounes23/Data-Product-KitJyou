import sys
import json
from math import exp
from dateutil import parser as date_parser
from datetime import datetime
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
    end_date = date_parser.isoparse(date_range.get("end", datetime.now().isoformat() + "Z"))
    
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

# Sort the combined results based on the given sort_type
def sort_aoss_results(results, sort_type, desc=True):
    """
    Sort a list of JSON objects based on the given sort_type.
    
    Parameters:
        results (str or list): JSON string or list of dictionaries to be sorted.
        sort_type (str): Sorting criteria ('dateModified', 'alphaByTitle', 'relevance').
        desc (bool): Sort order, descending if True (default).
    
    Returns:
        str: JSON string of sorted results.
    """

    # If results is a JSON string, try to parse it
    if isinstance(results, str):
        try:
            results = json.loads(results)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    # Ensure results is a list
    if not isinstance(results, list):
        raise TypeError(f"Expected a list, but got {type(results)}")

    # Validate sort_type
    valid_sort_types = {'dateModified', 'alphaByTitle', 'relevance'}

    if sort_type not in valid_sort_types:
        print("Invalid sort type. Defaulting to 'dateModified'")
        sort_type = 'dateModified'


    # Sort based on the sort_type
    if sort_type == 'dateModified':

        results.sort(
            key=lambda x: datetime.fromisoformat(
                x.get('modifyDate', '1970-01-01T00:00:00Z') 
            ), reverse=desc)
        
    elif sort_type == 'alphaByTitle':
        results.sort(key=lambda x: x.get('title', ''), reverse=not desc)

    elif sort_type == 'relevance':
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=desc)

    for i, docket in enumerate(results):
        docket["search_rank"] = i

    # Return sorted results as a JSON string
    return results

def drop_previous_results(searchTerm, sessionID, sortParams, filterParams):
    
    conn = connect()

    try:
        with conn.cursor() as cursor:
            delete_query = """
            DELETE FROM stored_results
            WHERE search_term = %s AND session_id = %s AND sort_asc = %s AND sort_type = %s
            AND filter_agencies = %s AND filter_date_start = %s AND filter_date_end = %s AND filter_rulemaking = %s
            """
            cursor.execute(delete_query, (searchTerm, sessionID, sortParams["desc"], sortParams["sortType"],
                                          ",".join(sorted(filterParams["agencies"])) if filterParams["agencies"] else '', filterParams["dateRange"]["startDate"],
                                          filterParams["dateRange"]["endDate"], filterParams["docketType"]))
    except Exception as e:
        print(f"Error deleting previous results for search term {searchTerm}")
        print(e)

    conn.commit()
    conn.close()

def storeDockets(dockets, searchTerm, sessionID, sortParams, filterParams, totalResults):

    conn = connect()

    for i in range(min(totalResults, len(dockets))):
        values = (
            searchTerm,
            sessionID,
            sortParams["desc"],
            sortParams["sortType"],
            ",".join(sorted(filterParams["agencies"])) if filterParams["agencies"] else '',
            filterParams["dateRange"]["startDate"],
            filterParams["dateRange"]["endDate"],
            filterParams["docketType"],
            i,
            dockets[i]["docketID"],
            dockets[i]["doc_count"],
            dockets[i]["matching_comments"],
            dockets[i]["relevance_score"]
        )

        # Insert into the database
        try:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO stored_results (
                    search_term, session_id, sort_asc, sort_type, filter_agencies, filter_date_start,
                    filter_date_end, filter_rulemaking, search_rank, docket_id, total_comments, matching_comments,
                    relevance_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, values)
        except Exception as e:
            print(f"Error inserting docket {dockets[i]['docketID']}")
            print(e)

    conn.commit()
    conn.close()

def getSavedResults(searchTerm, sessionID, sortParams, filterParams):
    
    conn = connect()

    try:
        with conn.cursor() as cursor:
            select_query = """
            SELECT search_rank, docket_id, total_comments, matching_comments, relevance_score FROM stored_results
            WHERE search_term = %s AND session_id = %s AND sort_asc = %s AND sort_type = %s AND filter_agencies = %s
            AND filter_date_start = %s AND filter_date_end = %s AND filter_rulemaking = %s
            """
            cursor.execute(select_query, (searchTerm, sessionID, sortParams["desc"], sortParams["sortType"],
                                          ",".join(sorted(filterParams["agencies"])) if filterParams["agencies"] else '', filterParams["dateRange"]["startDate"],
                                          filterParams["dateRange"]["endDate"], filterParams["docketType"]))
            dockets = cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving dockets for search term {searchTerm}")
        print(e)

    return dockets

def calc_relevance_score(docket):
    try:
        total_comments = docket.get("doc_count", 0)
        matching_comments = docket.get("matching_comments", 0)
        ratio = matching_comments / total_comments if total_comments > 0 else 0
        modify_date = date_parser.isoparse(docket.get("modifyDate", "1970-01-01T00:00:00Z"))
        age_days = (datetime.now() - modify_date).days
        decay = exp(-age_days / 365)
        return total_comments * (ratio ** 2) * decay
    except Exception as e:
        print(f"Error calculating relevance score for docket {docket.get('docketID', 'unknown')}: {e}")
        return 0

def query(search_params):

    search_params = json.loads(search_params)

    searchTerm = search_params["searchTerm"]
    pageNumber = query_params["pageNumber"]
    refreshResults = query_params["refreshResults"]
    sessionID = query_params["sessionID"]
    sortParams = query_params["sortParams"]
    filterParams = query_params["filterParams"]

    perPage = 10
    pages = 10
    totalResults = perPage * pages

    if refreshResults:

        drop_previous_results(searchTerm, sessionID, sortParams, filterParams)

        os_results = query_OpenSearch(searchTerm)
        results = append_docket_titles(os_results, connect())

        for docket in results:
            docket["relevance_score"] = calc_relevance_score(docket)

        filtered_results = filter_dockets(results, search_params.get('filterParams'))
    
        sorted_results = sort_aoss_results(filtered_results, search_params.get('sortParams').get('sortType'))

        storeDockets(sorted_results, searchTerm, sessionID, sortParams, filterParams, totalResults)

        return json.dumps(sorted_results[perPage * pageNumber:perPage * (pageNumber + 1)])

    else:
        dockets_raw = getSavedResults(searchTerm, sessionID, sortParams, filterParams)
        dockets = []
        for d in dockets_raw:
            dockets.append({
                "search_rank": d[0],
                "docketID": d[1],
                "doc_count": d[2],
                "matching_comments": d[3],
                "relevance_score": d[4]
            })
        dockets = sorted(dockets, key=lambda x: x["relevance_score"])
        dockets = dockets[perPage * pageNumber:perPage * (pageNumber + 1)]
        dockets = append_docket_titles(dockets, connect())
        return json.dumps(dockets)

if __name__ == '__main__':
    query_params = {
        "searchTerm": "gun",
        "pageNumber": 0,
        "refreshResults": False,
        "sessionID": "session1",
        "sortParams": {
            "sortType": "dateModified",
            "desc": True,
        },
        "filterParams": {
            "agencies": [],
            "dateRange": {
                "startDate": "1970-01-01",
                "endDate": "2025-03-21"
            },
            "docketType": ""
        }
    }

    searchTerm = query_params["searchTerm"]
    print(f"searchTerm: {searchTerm}")

    print(query(json.dumps(query_params)))

