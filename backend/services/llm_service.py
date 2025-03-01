from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import logging
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

# Initialize LLM
def get_llm():
    """Initialize and return the LLM instance"""
    return OpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS
    )

def generate_feedback(criteria_text, homework_text, relevant_context=None):
    """
    Generate feedback and marks for a student's homework using the LLM.
    
    Args:
        criteria_text (str): Text from the marking criteria PDF
        homework_text (str): Text from the student's homework PDF
        relevant_context (str, optional): Additional context from RAG
        
    Returns:
        tuple: (feedback, marks)
    """
    logger.info("Generating feedback using LLM")
    
    # Create base prompt
    base_prompt = """
    You are an AI assistant designed to grade student homework based on provided marking criteria.
    
    ## Marking Criteria:
    {criteria_text}
    
    ## Student Submission:
    {homework_text}
    
    """
    
    # Add relevant context if available
    if relevant_context:
        base_prompt += """
        ## Additional Context:
        {relevant_context}
        """
    
    # Complete the prompt with instructions
    base_prompt += """
    Based on the marking criteria and the student's submission, provide:
    
    1. Detailed feedback on the submission, highlighting strengths and areas for improvement
    2. A numerical mark or grade according to the marking criteria
    3. Specific recommendations for how the student can improve their work
    
    Format your response as follows:
    
    MARK: [numerical mark]
    
    FEEDBACK:
    [Your detailed feedback here]
    
    RECOMMENDATIONS:
    [Your specific recommendations for improvement]
    """
    
    # Create the prompt template
    prompt_template = PromptTemplate(
        input_variables=["criteria_text", "homework_text", "relevant_context"] if relevant_context else ["criteria_text", "homework_text"],
        template=base_prompt
    )
    
    # Format the prompt
    if relevant_context:
        prompt = prompt_template.format(
            criteria_text=criteria_text,
            homework_text=homework_text,
            relevant_context=relevant_context
        )
    else:
        prompt = prompt_template.format(
            criteria_text=criteria_text,
            homework_text=homework_text
        )
    
    # Get LLM and generate response
    llm = get_llm()
    response = llm(prompt)
    
    try:
        # Parse the response to extract mark and feedback
        mark_line = response.split("MARK:")[1].split("\n")[0].strip()
        feedback_section = response.split("FEEDBACK:")[1].split("RECOMMENDATIONS:")[0].strip()
        recommendations = response.split("RECOMMENDATIONS:")[1].strip()
        
        # Clean up and format the mark
        try:
            mark = float(mark_line)
        except ValueError:
            mark = mark_line
        
        # Combine feedback and recommendations
        full_feedback = f"{feedback_section}\n\nRECOMMENDATIONS:\n{recommendations}"
        
        return full_feedback, mark
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return response, "N/A" 