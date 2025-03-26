from create_client import create_client
import sys

client = create_client()

index_name = "comments_extracted_text"

# Get the search term from the command line
if len(sys.argv) < 2:
    print("Please provide a search term")
    sys.exit(1)


search_term = sys.argv[1]
print(f"Searching for: {search_term}")

query = {
    "size": 0,
    "aggs": 
    {
        "docketId_stats": 
        {
            "terms": 
            {
                "field": "docketId.keyword",  # Use .keyword for exact match on text fields
                "size": 1000 # number of matching extracted texts to return
            },
            "aggs": 
            {
                "matching_attachments": 
                {
                    "filter": {
                        "match": {
                                "extractedText": search_term # Searches in any text block
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
dockets = response["aggregations"]["docketId_stats"]["buckets"]

# Get the total number of documents in the index
index_stats = client.count(index=index_name)
total_documents = index_stats["count"]

# Create a list of comments in json format that contains the commentId, the number of total documents, and the number of matching terms in the extracted text

dockets = [
    {
        "docketId": docket["key"],
        "document_count": docket["document_count"],
        "matching_attachments": docket["matching_attachments"]["document_count"]
    }
    
    for docket in dockets
    ]

# Total number of extracted text documents that contain the search term 
total_attachments = sum(docket.get("document_count", 0) for docket in dockets)