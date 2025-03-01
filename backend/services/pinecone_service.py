import pinecone
import logging
from langchain.embeddings import OpenAIEmbeddings
from config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        # Initialize Pinecone client
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )
        
        # Check if index exists, create if it doesn't
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
        
        # Connect to index
        self.index = pinecone.Index(PINECONE_INDEX_NAME)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        logger.info("Pinecone service initialized successfully")
    
    def index_criteria(self, criteria_text, metadata=None):
        """
        Index the marking criteria text in Pinecone.
        
        Args:
            criteria_text (str): Text from marking criteria PDF
            metadata (dict, optional): Additional metadata about the criteria
            
        Returns:
            str: ID of the indexed item
        """
        try:
            # Create unique ID for this criteria
            criteria_id = f"criteria_{metadata.get('assignment_id', 'unknown')}"
            
            # Generate embedding for the text
            embedding = self.embeddings.embed_query(criteria_text)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata["text"] = criteria_text[:1000]  # Store truncated text in metadata
            metadata["type"] = "marking_criteria"
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(criteria_id, embedding, metadata)]
            )
            
            logger.info(f"Successfully indexed criteria with ID: {criteria_id}")
            return criteria_id
        
        except Exception as e:
            logger.error(f"Error indexing criteria: {str(e)}")
            raise
    
    def query_similar_content(self, query_text, top_k=3):
        """
        Query Pinecone for content similar to the query.
        
        Args:
            query_text (str): Text to find similar content for
            top_k (int): Number of results to return
            
        Returns:
            list: List of similar documents with their text and metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract and return results
            similar_items = []
            for match in results.matches:
                similar_items.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
                })
            
            logger.info(f"Found {len(similar_items)} similar items for query")
            return similar_items
        
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            return [] 