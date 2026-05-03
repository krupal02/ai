import json
import os
import re

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

class RAGService:
    def __init__(self, data_path="Data/airport_knowledge.json"):
        self.data_path = data_path
        self.documents = []
        self.initialize_vector_store()

    def _parse_json_dynamically(self, data, parent_key=""):
        documents = []
        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    documents.extend(self._parse_json_dynamically(v, new_key))
                else:
                    content = f"The {k} of {parent_key} is {v}." if parent_key else f"{k}: {v}"
                    documents.append(Document(page_content=content, metadata={"source": new_key}))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    documents.extend(self._parse_json_dynamically(item, f"{parent_key}[{i}]"))
                else:
                    documents.append(Document(page_content=f"{parent_key}[{i}]: {item}", metadata={"source": parent_key}))
        return documents

    def initialize_vector_store(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Knowledge file not found at {self.data_path}")
            
        print("Loading local knowledge base...")
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.documents = self._parse_json_dynamically(data)

    def retrieve_context(self, query, k=5):
        if not self.documents:
            return ""
            
        # Simple Keyword Matching
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return ""
            
        scored_docs = []
        for doc in self.documents:
            doc_words = set(re.findall(r'\w+', doc.page_content.lower()))
            score = len(query_words.intersection(doc_words))
            
            # Boost score if the query words appear as an exact substring
            if any(qw in doc.page_content.lower() for qw in query_words if len(qw) > 3):
                score += 2
                
            if score > 0:
                scored_docs.append((score, doc))
                
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for score, doc in scored_docs[:k]]
        
        context = "\n".join([doc.page_content for doc in top_docs])
        return context

# For testing
if __name__ == "__main__":
    service = RAGService()
    print(service.retrieve_context("Where is Starbucks?"))
