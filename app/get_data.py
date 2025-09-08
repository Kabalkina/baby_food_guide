import pandas as pd

import os

from dotenv import load_dotenv
import os
from groq import Groq
from qdrant_client import QdrantClient, models

from config_loader import DATA_PATH, QD_CLIENT, MODEL, COLLECTION_NAME, EMBEDDING_DIMENSIONALITY

def load_data(path=DATA_PATH):
    df = pd.read_csv(path, sep=';')
    documents = df.to_dict(orient='records')
    return documents


def create_collection_and_upsert(documents, model=MODEL, collection_name=COLLECTION_NAME):
    load_dotenv()
    
    QD_CLIENT.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=EMBEDDING_DIMENSIONALITY,
            distance=models.Distance.COSINE
        )
    )

    QD_CLIENT.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="id",
        field_schema="keyword"
    )

    points = []

    for i, doc in enumerate(documents):
        text = ' '.join(str(doc.get(field, "")) for field in df.columns if field != "id")

        vector = models.Document(text=text, model=model)
        point = models.PointStruct(
            id=i,
            vector=vector,
            payload=doc
        )
        points.append(point)

        QD_CLIENT.upsert(
        collection_name=collection_name,
        points=points
    )
    
    return QD_CLIENT
        



