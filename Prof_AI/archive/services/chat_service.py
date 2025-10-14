"""
Chat Service - Simplified direct LLM conversations with multilingual support
"""

import time
import logging
from typing import Dict, Any
import config
from services.llm_service import LLMService
from services.sarvam_service import SarvamService
from services.aum_counselor_service import AUMCounselorService

class ChatService:
    """Simplified chat service using direct LLM calls without RAG complexity."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.sarvam_service = SarvamService()
        
        # Initialize AUM counselor service
        try:
            self.aum_counselor_service = AUMCounselorService()
            self.is_aum_counselor_active = True
            logging.info("✅ AUM Counselor Service initialized")
        except Exception as e:
            logging.error(f"Failed to initialize AUM Counselor Service: {e}")
            self.aum_counselor_service = None
            self.is_aum_counselor_active = False
        
        logging.info("✅ Simplified Chat Service initialized (RAG disabled)")

    async def ask_question(self, query: str, query_language_code: str = "en-IN") -> Dict[str, Any]:
        """Answer all questions using AUM Counselor Service exclusively."""
        
        response_lang_name = next(
            (lang["name"] for lang in config.SUPPORTED_LANGUAGES if lang["code"] == query_language_code), 
            "English"
        )

        # Always use AUM Counselor Service for all queries
        if self.is_aum_counselor_active:
            logging.info("[TASK] Routing ALL queries to AUM Counselor Service...")
            start_time = time.time()
            
            try:
                # Translate query to English if needed for AUM counselor
                english_query = query
                if query_language_code != "en-IN":
                    logging.info("[TASK] Translating query to English for AUM counselor...")
                    english_query = await self.sarvam_service.translate_text(
                        text=query,
                        source_language_code=query_language_code,
                        target_language_code="en-IN"
                    )
                
                # Get response from AUM counselor service
                aum_response = await self.aum_counselor_service.get_counseling_response(
                    english_query, response_lang_name
                )
                
                end_time = time.time()
                logging.info(f"  > AUM Counselor response complete in {end_time - start_time:.2f}s.")
                
                # Translate response back if needed
                if query_language_code != "en-IN" and response_lang_name != "English":
                    logging.info("[TASK] Translating AUM response back to target language...")
                    translated_answer = await self.sarvam_service.translate_text(
                        text=aum_response["answer"],
                        source_language_code="en-IN",
                        target_language_code=query_language_code
                    )
                    aum_response["answer"] = translated_answer
                
                return aum_response
                
            except Exception as e:
                logging.error(f"  > Error in AUM Counselor Service: {e}")
                # Return AUM-branded error response instead of falling back
                return {
                    "answer": "Hello! I'm Alex from Auburn University at Montgomery. I'm experiencing technical difficulties right now, but I'm here to help with information about AUM programs, admissions, and student life. Please try your question again in a moment.",
                    "sources": ["AUM Counselor - Technical Issue"],
                    "counselor": "Alex - AUM International Admission Counselor",
                    "error": str(e)
                }
        else:
            # AUM Counselor service not available
            logging.error("[TASK] AUM Counselor Service not available!")
            return {
                "answer": "Hello! I'm Alex from Auburn University at Montgomery. I'm currently offline for maintenance, but I'll be back soon to help with your questions about AUM programs and admissions. Please visit aum.edu for immediate assistance.",
                "sources": ["AUM Counselor - Service Unavailable"],
                "counselor": "Alex - AUM International Admission Counselor"
            }
