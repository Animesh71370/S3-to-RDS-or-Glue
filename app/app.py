import json
import boto3
import pymysql
import os

# AWS clients
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')
glue_client = boto3.client('glue')

def read_s3_data(bucket_name, file_key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error reading S3 file: {e}")
        return None

def push_to_rds(data, db_params):
    try:
        connection = pymysql.connect(
            host=db_params['host'],
            user=db_params['user'],
            password=db_params['password'],
            database=db_params['database']
        )
        with connection.cursor() as cursor:
            # Modify this according to your actual data structure
            cursor.execute("INSERT INTO your_table (column1, column2) VALUES (%s, %s)", (data, data))
            connection.commit()
        return {"status": "success", "message": "Data pushed to RDS successfully."}
    except Exception as e:
        print(f"RDS push failed: {str(e)}")
        return {"status": "error", "message": f"RDS push failed: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()

def push_to_glue(data, glue_db, glue_table):
    try:
        glue_client.batch_create_partition(
            DatabaseName=glue_db,
            TableName=glue_table,
            PartitionInputList=[{"Values": [data]}]
        )
        return {"status": "success", "message": "Data pushed to Glue successfully."}
    except Exception as e:
        print(f"Glue push failed: {str(e)}")
        return {"status": "error", "message": f"Glue push failed: {str(e)}"}

# Main Lambda handler function
def lambda_handler(event, context):
    # For local testing or when event is not provided
    bucket_name = os.getenv('S3_BUCKET', event.get('bucket_name'))
    file_key = os.getenv('S3_KEY', event.get('file_key'))
    
    db_params = {
        'host': os.getenv('RDS_HOST'),
        'user': os.getenv('RDS_USER'),
        'password': os.getenv('RDS_PASSWORD'),
        'database': os.getenv('RDS_DATABASE')
    }
    
    glue_db = os.getenv('GLUE_DATABASE')
    glue_table = os.getenv('GLUE_TABLE')

    # Validate required parameters
    if not all([bucket_name, file_key, db_params['host'], db_params['user'], db_params['password'], db_params['database']]):
        return {
            "status": "error",
            "message": "Missing required configuration parameters"
        }

    # Read data from S3
    data = read_s3_data(bucket_name, file_key)
    if not data:
        return {
            "status": "error", 
            "message": "Failed to read data from S3"
        }

    # Attempt to push to RDS
    rds_result = push_to_rds(data, db_params)
    
    # If RDS push fails, try Glue
    if rds_result['status'] == 'error':
        glue_result = push_to_glue(data, glue_db, glue_table)
        return glue_result

    return rds_result

# For local testing
if __name__ == "__main__":
    # You can add local testing logic here
    print("Lambda function is ready.")
