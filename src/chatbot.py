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
            # Try fallback response if:
            # 1. No API key is set, or
            # 2. It's the default API key, or
            # 3. We're in test/demo mode
            if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
                print("No API key set, using fallback responses")
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
        
        # Main company information
        if "what does able do" in query_lower or "services" in query_lower or "what is able" in query_lower:
            return "Able is a full-service digital product agency that partners with funded startups and established brands to build innovative, user-focused digital products. We provide end-to-end services from strategy and discovery through design, development, and growth."
        
        # Team information
        elif "teams" in query_lower or "who works" in query_lower or "employees" in query_lower:
            return "Able has multidisciplinary teams across several key areas: Product Management, Design, Engineering, and Strategy. Our teams collaborate closely with clients as true partners throughout the product development lifecycle."
        
        # Industry information
        elif "industries" in query_lower or "clients" in query_lower or "sectors" in query_lower:
            return "Able works across various industries including fintech, healthcare, education, media, retail, and enterprise software. We've built payment platforms, telemedicine solutions, learning management systems, content delivery platforms, and more."
        
        # Mission information
        elif "mission" in query_lower or "values" in query_lower or "purpose" in query_lower:
            return "Able's mission is to help organizations transform their ideas into exceptional digital products that create value for users and drive business growth. We believe in user-centered design, technical excellence, and true partnership with our clients."
        
        # Location information
        elif "located" in query_lower or "location" in query_lower or "where" in query_lower or "office" in query_lower:
            return "Able is headquartered in New York City, with team members distributed across the United States and globally. Our global presence allows us to work with clients around the world and build diverse teams with varied perspectives."
        
        # Website information
        elif "website" in query_lower or "url" in query_lower or "site" in query_lower:
            return "Able's official website is available at https://able.co. You can find more information about our services, case studies, and team there."
        
        # Contact information
        elif "contact" in query_lower or "email" in query_lower or "phone" in query_lower or "reach" in query_lower:
            return "You can contact Able through their website at https://able.co/contact. They also have a presence on social media platforms such as LinkedIn, Twitter, and Instagram."
        
        # Process information
        elif "process" in query_lower or "methodology" in query_lower or "approach" in query_lower:
            return "Able follows a collaborative, iterative approach to product development that typically includes discovery and strategy, design, engineering, testing, and deployment phases. We emphasize close client collaboration throughout the process."
        
        # Technology information
        elif "technology" in query_lower or "tech stack" in query_lower or "programming" in query_lower or "languages" in query_lower:
            return "Able's engineering teams work with various technologies including React, React Native, Node.js, Python, and more. We select the appropriate technology stack based on each project's specific requirements and client needs."
        
        # General fallback
        else:
            return "I'm the Able support chatbot. I can answer questions about Able's services, teams, industries, mission, technologies, locations, and more. How can I help you today?"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the conversation history for display"""
        return self.memory.get_chat_history()
