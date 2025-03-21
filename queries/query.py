from datetime import datetime
from utils.query_opensearch import query_OpenSearch
from utils.query_sql import append_docket_titles
from utils.sql import connect
import json
import sys


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
                x.get('dateModified', '1900-01-01T00:00:00Z') 
            ), reverse=desc)
        
    elif sort_type == 'alphaByTitle':
        results.sort(key=lambda x: x.get('title', ''), reverse=not desc)

    # Return sorted results as a JSON string
    return json.dumps(results)


# Query the OpenSearch API and append docket supplementary information
def query(search_params): 
    os_results = query_OpenSearch(search_params.get('searchTerm'))

    print(os_results)

    combined_results = append_docket_titles(os_results, connect())

    return sort_aoss_results(combined_results, search_params.get('sortParams').get('sortType'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a search term")
        sys.exit(1)

    search_term = sys.argv[1]
    print(f"search_term: {search_term}")
    print(query(search_params))
