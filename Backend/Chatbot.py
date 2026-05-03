import requests
from Backend.RAGService import RAGService

class ChatBot:
    def __init__(self):
        self.rag_service = RAGService()
        self.model_name = "qwen2.5:0.5b"
        print(f"ChatBot initialized to use local Ollama model: {self.model_name}")

    def _build_system_prompt(self, user_profile: str, location_context: str, context: str) -> str:
        """Build a context-aware system prompt based on user profile data."""
        
        base = (
            "You are AeroGuide, an AI Airport Companion. You are helpful, polite, and concise. "
            "Use the provided context to answer the user's query. If you don't know the answer, say you don't know. "
            "CRITICAL RULE: No matter what language the user speaks (e.g. Hindi, Hinglish), "
            "you MUST always reply in pure, correct ENGLISH. Do not use Hindi text."
        )

        # Parse profile string for personalization
        profile_lower = user_profile.lower()

        # Travel frequency adaptation
        if 'first_time' in profile_lower or 'first-time' in profile_lower:
            base += (
                "\n\nThe user is a FIRST-TIME FLYER. Provide:"
                "\n- Detailed step-by-step instructions"
                "\n- Explanations of airport terminology (gates, boarding pass, etc.)"
                "\n- Extra reassurance and encouragement"
                "\n- Proactive warnings about common mistakes"
                "\n- Suggest arriving extra early"
            )
        elif 'frequent' in profile_lower:
            base += (
                "\n\nThe user is a FREQUENT FLYER. Provide:"
                "\n- Concise, direct information without over-explaining basics"
                "\n- Shortcuts and time-saving tips"
                "\n- Lounge access information when relevant"
                "\n- Priority lane suggestions"
                "\n- Assume familiarity with airport procedures"
            )
        elif 'occasional' in profile_lower:
            base += (
                "\n\nThe user is an OCCASIONAL TRAVELER. Provide:"
                "\n- Clear information with moderate detail"
                "\n- Gentle reminders of important steps"
                "\n- Highlight any changes since last travel season"
            )

        # Age-based adaptation
        if '65+' in profile_lower or 'senior' in profile_lower:
            base += (
                "\n\nThe user is a SENIOR CITIZEN. Provide:"
                "\n- Slower-paced, patient guidance"
                "\n- Information about wheelchair and buggy services"
                "\n- Rest area locations nearby"
                "\n- Add extra time buffers in all walking estimates"
            )

        # Dietary awareness
        if 'diet:' in profile_lower or 'dietary' in profile_lower:
            # Extract dietary info
            if 'veg' in profile_lower and 'non' not in profile_lower:
                base += "\n\nThe user is VEGETARIAN. Only recommend vegetarian food options."
            elif 'vegan' in profile_lower:
                base += "\n\nThe user is VEGAN. Only recommend vegan food options."
            elif 'jain' in profile_lower:
                base += "\n\nThe user is JAIN. Only recommend Jain-friendly food (no root vegetables, onion, garlic)."

        # Special assistance
        if 'wheelchair' in profile_lower:
            base += "\n\nThe user needs WHEELCHAIR ASSISTANCE. Prioritize accessible routes and elevator locations."
        if 'visual' in profile_lower:
            base += "\n\nThe user has VISUAL IMPAIRMENT. Provide detailed verbal directions with landmarks."
        if 'infant' in profile_lower:
            base += "\n\nThe user is TRAVELING WITH AN INFANT. Mention baby care rooms, family lanes, and stroller policies."

        # Inject context
        base += f"\n\nUser Profile/Status: {user_profile}"
        base += f"\n\nExact Passenger Location: {location_context}"
        base += f"\n\nContext Information:\n{context}"

        return base

    def get_response(self, query: str, user_profile: str, latitude: float = None, longitude: float = None) -> str:
        # Retrieve relevant context from RAG
        print("DEBUG: Calling rag_service.retrieve_context...")
        try:
            context = self.rag_service.retrieve_context(query)
            print("DEBUG: Context retrieved.")
        except Exception as e:
            print(f"DEBUG: RAG failed: {e}")
            context = ""
        
        # Mock Location Mapping
        location_context = "Unknown Location"
        if latitude and longitude:
            # We are mocking the indoor mapping for the hackathon
            location_context = "Terminal 2, Near Security Checkpoint (Coordinates tracking active)"

        system_prompt = self._build_system_prompt(user_profile, location_context, context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            print("DEBUG: Sending request to Ollama...")
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 256
                }
            }
            
            print("DEBUG: Request sent, waiting for response...")
            response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=5)
            print(f"DEBUG: Ollama response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            return data["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to local Ollama. Is Ollama running?"
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"

# For testing
if __name__ == "__main__":
    bot = ChatBot()
    print(bot.get_response("Where is starbucks?", "Name: Raj, Travel Type: first_time, Age Group: 18-30, Diet: veg"))
