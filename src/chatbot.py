import os
import json
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Message:
    """Represents a message in a conversation"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format for OpenAI API"""
        return {
            "role": self.role,
            "content": self.content
        }

class ConversationMemory:
    """Manages conversation history"""
    def __init__(self, max_tokens: int = 4000):
        self.messages: List[Message] = []
        self.max_tokens = max_tokens
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.messages.append(Message(role, content))
        # In a more sophisticated implementation, we would track token count
        # and trim older messages if needed to stay under max_tokens
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation history in API format"""
        return [message.to_dict() for message in self.messages]
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get formatted chat history for display"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

class AbleSupportChatbot:
    """Main chatbot class that processes queries and generates responses"""
    def __init__(self, retriever=None):
        self.retriever = retriever
        self.memory = ConversationMemory()
        
        # Check for API key
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
            print("Warning: OpenAI API key not set or using default value. Set it in the .env file.")
    
    def get_response(self, query: str) -> str:
        """Process user query and return chatbot response"""
        # Add user message to memory
        self.memory.add_message("user", query)
        
        # Retrieve relevant context if retriever is available
        context = self._retrieve_context(query) if self.retriever else ""
        
        # Generate response using OpenAI API with context
        response = self._generate_response(query, context)
        
        # Add assistant response to memory
        self.memory.add_message("assistant", response)
        
        return response
    
    def _retrieve_context(self, query: str) -> str:
        """Retrieve relevant context for the query"""
        try:
            documents = self.retriever.get_relevant_documents(query)
            
            # Format context from retrieved documents
            context_parts = []
            for doc in documents:
                source = doc["metadata"].get("source", "unknown")
                section = doc["metadata"].get("section", "unknown")
                content = doc["content"]
                context_parts.append(f"Source: {source} (Section: {section})\nContent: {content}\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate a response using OpenAI API with the provided context"""
        try:
            if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
                return self._get_fallback_response(query)
            
            # Set up messages for the API
            messages = [
                {"role": "system", "content": f"""You are a helpful customer support chatbot for Able, a digital product agency. 
                Answer user questions based on the following context. Be concise and accurate.
                If you don't know the answer based on the context provided, admit that you don't know rather than making something up.
                
                Context about Able:
                {context}"""}
            ]
            
            # Add conversation history
            messages.extend(self.memory.get_messages()[:-1])  # Exclude the last user message we just added
            
            # Add the user's current query
            messages.append({"role": "user", "content": query})
            
            # Call OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 300
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(query)
    
    def _get_fallback_response(self, query: str) -> str:
        """Get a fallback response when API is not available"""
        # Simple keyword matching fallback system
        query_lower = query.lower()
        
        if "what does able do" in query_lower or "services" in query_lower:
            return "Able is a full-service digital product agency that partners with funded startups and established brands to build innovative, user-focused digital products."
        
        elif "teams" in query_lower:
            return "Able has multidisciplinary teams across several key areas: Product Management, Design, Engineering, and Strategy."
        
        elif "industries" in query_lower:
            return "Able works across various industries including fintech, healthcare, education, media, retail, and enterprise software."
        
        elif "mission" in query_lower:
            return "Able's mission is to help organizations transform their ideas into exceptional digital products that create value for users and drive business growth."
        
        elif "located" in query_lower or "location" in query_lower:
            return "Able is headquartered in New York City, with team members distributed across the United States and globally."
        
        else:
            return "I'm the Able support chatbot. I can answer questions about Able's services, teams, industries we work with, our mission, and locations. How can I help you today?"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the conversation history for display"""
        return self.memory.get_chat_history()
