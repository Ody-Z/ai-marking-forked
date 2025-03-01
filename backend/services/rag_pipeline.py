import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.pinecone_service import PineconeService
from services.llm_service import generate_feedback

logger = logging.getLogger(__name__)

def process_homework(criteria_text, homework_text):
    """
    Process a student's homework using RAG to generate feedback.
    
    Args:
        criteria_text (str): Text from the marking criteria PDF
        homework_text (str): Text from the student's homework PDF
        
    Returns:
        tuple: (feedback, marks)
    """
    logger.info("Starting RAG pipeline processing")
    
    try:
        # Initialize Pinecone service
        pinecone_service = PineconeService()
        
        # Index the criteria for future reference
        pinecone_service.index_criteria(criteria_text, {"source": "current_assignment"})
        
        # Split homework into chunks for processing
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150
        )
        homework_chunks = text_splitter.split_text(homework_text)
        
        # For each chunk, find relevant criteria contexts
        all_contexts = []
        for chunk in homework_chunks:
            similar_items = pinecone_service.query_similar_content(chunk)
            for item in similar_items:
                all_contexts.append(item["text"])
        
        # Deduplicate and combine contexts
        unique_contexts = list(set(all_contexts))
        combined_context = "\n\n".join(unique_contexts[:3])  # Limit to top 3 contexts
        
        # Generate feedback using LLM
        feedback, marks = generate_feedback(criteria_text, homework_text, combined_context)
        
        logger.info(f"Successfully processed homework with RAG pipeline, generated marks: {marks}")
        return feedback, marks
    
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        # Fallback to direct LLM processing without RAG
        logger.info("Falling back to direct LLM processing without RAG")
        return generate_feedback(criteria_text, homework_text) 