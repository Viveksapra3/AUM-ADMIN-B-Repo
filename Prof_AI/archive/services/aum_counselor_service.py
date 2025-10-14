"""
AUM Counselor Service - Specialized service for Auburn University at Montgomery admission counseling
Uses fine-tuned OpenAI model for accurate and contextual responses
"""

from openai import AsyncOpenAI
from typing import Dict, Any
import config
import logging

class AUMCounselorService:
    """Service for AUM admission counseling using fine-tuned OpenAI model."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            timeout=60.0
        )
        
        # Fine-tuned model specifically for AUM counseling (fallback to regular model for now)
        self.aum_model = "gpt-4o-mini"  # Using regular model until fine-tuned model is available
        # self.aum_model="ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T"  # Uncomment when available
        
        # System prompt for Alex, the AUM counselor
        self.system_prompt = """
          You are Alex, an experienced international admission counselor at
          Auburn University at Montgomery (AUM). You help prospective students
          from around the world understand AUM programs, admission process,
          visa support, scholarships, housing, and campus life.
          
          IMPORTANT RESPONSE GUIDELINES:
          - Keep responses SHORT and conversational (2-4 sentences max)
          - Use plain text only - NO bold formatting, NO bullet points, NO numbered lists
          - Be friendly, encouraging, and helpful like a real counselor
          - Focus only on AUM-specific information from your training
          - If you don't know something specific about AUM, suggest contacting the admissions office
          - Always be polite, encouraging, and factual as an official AUM representative
        """
        
        logging.info("✅ AUM Counselor Service initialized with fine-tuned model")
    
    async def get_counseling_response(self, query: str, target_language: str = "English") -> Dict[str, Any]:
        """Get a counseling response using the fine-tuned AUM model."""
        
        # Prepare messages for the fine-tuned model
        messages = [
            {
                "role": "system",
                "content": self.system_prompt.strip()
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        try:
            logging.info(f"[AUM COUNSELOR] Processing query with fine-tuned model: {query[:50]}...")
            
            response = await self.client.chat.completions.create(
                model=self.aum_model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent, focused responses
                max_tokens=200,   # Limit tokens to encourage shorter responses
                top_p=0.9        # Focus on most likely tokens
            )
            
            answer = response.choices[0].message.content
            
            logging.info(f"[AUM COUNSELOR] Response generated successfully: {len(answer)} characters")
            
            return {
                "answer": answer,
                "sources": ["AUM Fine-tuned Model"],
                "model_used": self.aum_model,
                "counselor": "Alex - AUM International Admission Counselor"
            }
            
        except Exception as e:
            logging.error(f"[AUM COUNSELOR] Error getting response: {e}")
            logging.error(f"[AUM COUNSELOR] Model used: {self.aum_model}")
            logging.error(f"[AUM COUNSELOR] Query: {query[:100]}...")
            
            # Print the full error for debugging
            import traceback
            logging.error(f"[AUM COUNSELOR] Full error traceback: {traceback.format_exc()}")
            
            # Fallback response
            fallback_response = """
            Hello! I'm Alex from Auburn University at Montgomery. I'm currently experiencing 
            technical difficulties, but I'd be happy to help you with information about AUM's 
            programs, admissions, and student life. Please try your question again, or you can 
            visit our website at aum.edu for more information.
            """
            
            return {
                "answer": fallback_response.strip(),
                "sources": ["AUM Fallback Response"],
                "model_used": "fallback",
                "counselor": "Alex - AUM International Admission Counselor",
                "error": str(e)
            }
    
    def is_aum_related_query(self, query: str) -> bool:
        """Check if the query is related to AUM or university admissions."""
        aum_keywords = [
            "aum", "auburn university montgomery", "auburn montgomery",
            "admission", "admissions", "university", "college",
            "program", "programs", "course", "courses", "degree",
            "scholarship", "financial aid", "tuition", "fees",
            "visa", "f1", "student visa", "international student",
            "housing", "dormitory", "campus", "student life",
            "application", "apply", "requirements", "gpa",
            "toefl", "ielts", "sat", "act", "transcript",
            "enrollment", "semester", "academic", "faculty"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in aum_keywords)
