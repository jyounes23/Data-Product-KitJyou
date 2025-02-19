from IngestComment import insert_comment
from IngestDocket import insert_docket
from IngestDocument import insert_document
import boto3
import sys
import os
import psycopg
from dotenv import load_dotenv

def get_text_content_from_s3(bucket, file_key: str):
    try:
        obj = bucket.Object(file_key)
        text = obj.get()["Body"].read().decode("utf-8")
        return text
    except Exception as e:
        print(f"Error retrieving JSON file {file_key}, {e}")
        return None

def process_comments(bucket, conn, s3_path):
    text = get_text_content_from_s3(bucket, s3_path)
    insert_comment(conn, text)

def process_dockets(bucket, conn, s3_path):
    text = get_text_content_from_s3(bucket, s3_path)
    insert_docket(conn, text)

def process_documents(bucket, conn, s3_path):
    text = get_text_content_from_s3(bucket, s3_path)
    insert_document(conn, text)

def sort_files(files_list):
    category_order = {"docket": 1, "documents": 2, "comments": 3}
    def sorting_key(file_path):
        for category in category_order.keys():
            if category in file_path:
                return category_order[category]
        return float("inf")
    return sorted(files_list, key=sorting_key)

def categorize_and_process_files(bucket, conn, file_list):
    exclude_keywords = ["binary", "comments_extracted_text", "(1)"]
    for file_path in file_list:
        if all(keyword not in file_path for keyword in exclude_keywords):
            if "comments" in file_path:
                process_comments(bucket, conn, file_path)
            elif "docket" in file_path:
                process_dockets(bucket, conn, file_path)
            elif "documents" in file_path:
                process_documents(bucket, conn, file_path)
            else:
                print(f"Unknown category for file: {file_path}")

def get_s3_files(bucket):
    files = bucket.objects.all()
    return [file.key for file in files if file.key.endswith(".json")]

def main():
    bucket_name = "docket-samples"
    s3 = boto3.resource(service_name="s3", region_name="us-east-1")
    bucket = s3.Bucket(bucket_name)
    files = get_s3_files(bucket)
    sorted_files = sort_files(files)
  #  print(sorted_files)
    load_dotenv()
    conn_params = {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USERNAME"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
    }
    with psycopg.connect(**conn_params) as conn:
        categorize_and_process_files(bucket, conn, sorted_files)
        
if __name__ == "__main__":
    main()
