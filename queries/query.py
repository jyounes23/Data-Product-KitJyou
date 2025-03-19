from utils.query_opensearch import query_OpenSearch
from utils.query_sql import append_docket_titles
from utils.sql import connect

import sys

def query(search_term): 
    os_results = query_OpenSearch(search_term)
    print(os_results)
    return append_docket_titles(os_results, connect())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a search term")
        sys.exit(1)

    search_term = sys.argv[1]
    print(f"search_term: {search_term}")
    print(query(search_term))
