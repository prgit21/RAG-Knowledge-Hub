from io import BytesIO
from minio import Minio

# Connect to the local MinIO server running via docker compose
client = Minio(
    "localhost:9001",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

bucket = "demo"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

# Upload a small text file from memory
content = BytesIO(b"Hello from MinIO!")
client.put_object(bucket, "hello.txt", content, length=content.getbuffer().nbytes)

# Retrieve the object and print its contents
response = client.get_object(bucket, "hello.txt")
print(response.read().decode())
response.close()
response.release_conn()

