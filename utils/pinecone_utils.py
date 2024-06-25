from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = 'a05e07fe-757d-4abd-b03f-0ca80aa192b7'
INDEX_NAME = 'property-index-cosine'

class PineconeManager:
    def __init__(self):
        self.pc=Pinecone(PINECONE_API_KEY)
        if INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(INDEX_NAME, dimension=768, metric='cosine',spec=ServerlessSpec(cloud='aws',region='us-east-1'))
        self.index = self.pc.Index(INDEX_NAME)

    def insert(self, id, vector):
        self.index.upsert([(str(id), vector)])

    def query(self, vector, top_k=10):
        return self.index.query(vector=[vector], top_k=top_k, include_metadata=True)

    def delete(self, id):
        self.index.delete(ids=[str(id)])
