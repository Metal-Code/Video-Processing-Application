from google.cloud import storage, firestore
import uuid
import os
from datetime import datetime
import streamlit as st

def init_gcp_clients():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
    storage_client = storage.Client()
    firestore_client = firestore.Client()
    return storage_client, firestore_client

def upload_to_gcs(bucket_name, local_path, original_name):
    storage_client, firestore_client = init_gcp_clients()
    bucket = storage_client.bucket(bucket_name)
    video_id = str(uuid.uuid4())
    blob = bucket.blob(f"compressed/{video_id}.mp4")
    blob.upload_from_filename(local_path)
    blob.make_public()

    doc = {
        "id": video_id,
        "original_name": original_name,
        "filename": f"{video_id}.mp4",
        "upload_date": datetime.utcnow(),
        "size_mb": round(os.path.getsize(local_path) / (1024 * 1024), 2),
        "download_url": blob.public_url
    }

    firestore_client.collection("compressed_videos").document(video_id).set(doc)
    return doc
