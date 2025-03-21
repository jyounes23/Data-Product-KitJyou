from utils.query_opensearch import query_OpenSearch
from utils.query_sql import append_docket_titles
from utils.sql import connect

import json
import sys

def filter_dockets(dockets, filterParams):
    return dockets

def sort_aoss_results(dockets, sort_type, desc=True):
    return dockets

def storeDockets(dockets, searchTerm, sessionID, sortParams, filterParams, totalResults):

    conn = connect()

    for i in range(min(totalResults, len(dockets))):
        values = (
            searchTerm,
            sessionID,
            sortParams["desc"],
            sortParams["sortField"],
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

        print(values)

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

def getSavedResults(searchTerm, sessionID, sortParams, filterParams):
    
    conn = connect()

    try:
        with conn.cursor() as cursor:
            select_query = """
            SELECT search_rank, docket_id, total_comments, matching_comments, relevance_score FROM stored_results
            WHERE search_term = %s AND session_id = %s AND sort_asc = %s AND sort_type = %s AND filter_agencies = %s
            AND filter_date_start = %s AND filter_date_end = %s AND filter_rulemaking = %s
            """
            cursor.execute(select_query, (searchTerm, sessionID, sortParams["desc"], sortParams["sortField"],
                                          ",".join(sorted(filterParams["agencies"])) if filterParams["agencies"] else '', filterParams["dateRange"]["startDate"],
                                          filterParams["dateRange"]["endDate"], filterParams["docketType"]))
            dockets = cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving dockets for search term {searchTerm}")
        print(e)

    return dockets


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
        os_results = query_OpenSearch(searchTerm)
        dockets = json.loads(append_docket_titles(os_results, connect()))
        for d in dockets:
            # temporary relevance score
            d["relevance_score"] = 1
        dockets = filter_dockets(dockets, filterParams)
        dockets = sort_aoss_results(dockets, sortParams)

        storeDockets(dockets, searchTerm, sessionID, sortParams, filterParams, totalResults)

        return json.dumps(dockets[perPage * pageNumber:perPage * (pageNumber + 1)])

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
        return dockets

if __name__ == '__main__':
    query_params = {
        "searchTerm": "gun",
        "pageNumber": 1,
        "refreshResults": False,
        "sessionID": "session1",
        "sortParams": {
            "sortField": "dateModified",
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
