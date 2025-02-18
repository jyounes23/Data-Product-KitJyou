# OpenSearch Timing Data

We want to investigate how long querying millions of comments will take using our current query structure. If there will be a noticeable delay to the user, we will want to restructure our data and/or develop a new query to improve efficiency.

## Procedure

We used the following query that looks for the word "the" in comments. The word "the" was chosen so that, regardless of the actual content of a comment, we will likely get a match. The query is as follows:

```json
{
    "size": 0,
    "aggs": {
        "docketId_stats": {
            "terms": {
                "field": "docketId.keyword",
                "size": 1000
            },
            "aggs": {
                "matching_comments": {
                    "filter": {
                        "match": {
                            "commentText": "the"
                        }
                    }
                }
            }
        }
    }
}
```

Following the query, we collected the results that we would want to display to the user using the following code:

```python
# Extract the aggregation results
    dockets = response["aggregations"]["docketId_stats"]["buckets"]

    # Get the total number of documents in the index
    index_stats = client.count(index=index_name)
    total_documents = index_stats["count"]

    for docket in dockets:
        docket_id = docket["key"]
        total_comments = docket["doc_count"]
        matching_comments = docket["matching_comments"]["doc_count"]
```

We ran this process on indices containing 10, 50, 100, 500, and 1000 comments. For each size, the process was run once as a "warmup" to ensure that the connection to the local OpenSearch instance was initialized. Then, the process was run and timed 10 times for each size of indices.

## Results

The runtimes are shown in the following table, with times shown in seconds:

|             | 10 Comments | 50 Comments | 100 Commments | 500 Comments | 1000 Comments |
| ----------- | ----------- | ----------- | ------------- | ------------ | ------------- |
| Run 1       | 0.00845     | 0.00764     | 0.00719       | 0.00741      | 0.00619       |
| Run 2       | 0.00816     | 0.00809     | 0.00779       | 0.00847      | 0.00713       |
| Run 3       | 0.01276     | 0.00829     | 0.00831       | 0.00829      | 0.00604       |
| Run 4       | 0.00825     | 0.02471     | 0.00713       | 0.00956      | 0.00735       |
| Run 5       | 0.01109     | 0.01197     | 0.00905       | 0.00616      | 0.00651       |
| Run 6       | 0.01394     | 0.00847     | 0.00735       | 0.00790      | 0.00817       |
| Run 7       | 0.01135     | 0.00889     | 0.01156       | 0.00624      | 0.00698       |
| Run 8       | 0.00626     | 0.00861     | 0.02677       | 0.00681      | 0.00676       |
| Run 9       | 0.00875     | 0.00889     | 0.00853       | 0.00729      | 0.00707       |
| Run 10      | 0.00781     | 0.00859     | 0.00715       | 0.00720      | 0.00702       |
| **Average** | **0.00968** | **0.01041** | **0.01008**   | **0.00753**  | **0.00692**   |

From the above table, we do not see a significant slow-down when increasing the number of comments (in fact, there is a speed-up but there is no reason to think that it will continue to speed up with larger sizes). It could be valuable to test larger sample sizes, such as 5000 or 10000, to make sure that the query time remains approximately constant. However, from this exploration, it appears that querying millions of comments will not take significantly longer than querying a small number of comments.