# Note: This script of simply an outline of how the extracted text query can be implemented.

from create_client import create_client
import sys

client = create_client()

index_name = "extracted_text"

# Get the search term from the command line
if len(sys.argv) < 2:
    print("Please provide a search term")
    sys.exit(1)


search_term = sys.argv[1]
print(f"Searching for: {search_term}")

query = {
    "size": 0,  # No need to fetch individual documents
    "aggs": 
    {
        "docketId_stats": 
        {
            "terms": 
            {
                "field": "commentId.keyword",  # Use .keyword for exact match on text fields
                "size": 20 # number of matching extracted texts to return
            },
            "aggs": 
            {
                "matching_documents": 
                {
                    "filter": {
                        "bool": 
                        {
                            "should": 
                            [
                                {"match": {"extractedText": search_term}}  # Searches in any text block
                            ],
                            "minimum_should_match": 1  # Ensures at least one match
                        }
                    }
                }
            }
        }
    }
}

# Execute the query
response = client.search(index=index_name, body=query)

# Extract the aggregation results
comments = response["aggregations"]["docketId_stats"]["buckets"]

# Get the total number of documents in the index
index_stats = client.count(index=index_name)
total_documents = index_stats["count"]

# Create a list of comments in json format that contains the commentId, the number of total documents, and the number of matching terms in the extracted text

comments = [
    {
        "commentID": comment["key"],
        "document_count": comment["document_count"],
        "matching_documents": comment["matching_documents"]["document_count"]
    }
    
    for comment in comments
    ]

# Total number of extracted text documents that contain the search term 
total_attachments = sum(comment.get("document_count", 0) for comment in comments)