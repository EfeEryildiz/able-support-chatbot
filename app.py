import streamlit as st
import os
import time
from dotenv import load_dotenv
from src.scraper import scrape_able_website, get_fallback_data
from src.data_processor import process_scraped_data
from src.embeddings import create_vector_store
from src.chatbot import AbleSupportChatbot

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Able Support Chatbot",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        max-width: 90%;
    }
    .chat-message.user {
        background-color: #F0F2F6;
        margin-left: auto;
    }
    .chat-message.assistant {
        background-color: #E3F2FD;
        margin-right: auto;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 10px;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .st-emotion-cache-eczf16 {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Set up sidebar
with st.sidebar:
    st.title("Able Support Chatbot")
    st.markdown("---")
    st.markdown("""
    This chatbot can answer questions about Able such as:
    - What does Able do?
    - What kinds of teams does Able have?
    - What industries has Able worked with?
    - What is Able's mission?
    - Where is Able located?
    """)
    
    st.markdown("---")
    
    # Add OpenAI API key input
    api_key = st.text_input("OpenAI API Key (optional)", 
                            value=os.getenv("OPENAI_API_KEY", ""),
                            type="password",
                            help="Enter your OpenAI API key to enable the chatbot to generate responses using GPT. If not provided, the chatbot will use a fallback system.")
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Data preparation options
    st.markdown("## Data Options")
    data_option = st.radio(
        "Choose data source:",
        ["Use fallback data (quick start)", "Scrape Able website (takes longer)"]
    )
    
    # Initialize or refresh data button
    if st.button("Initialize/Refresh Data"):
        with st.spinner("Preparing data..."):
            if "Use fallback" in data_option:
                st.session_state.data_status = "Using fallback data..."
                get_fallback_data()
            else:
                st.session_state.data_status = "Scraping Able website..."
                try:
                    scrape_able_website()
                except Exception as e:
                    st.error(f"Error scraping website: {e}")
                    st.session_state.data_status = "Falling back to pre-defined data..."
                    get_fallback_data()
            
            st.session_state.data_status = "Processing data..."
            process_scraped_data()
            
            st.session_state.data_status = "Creating vector embeddings..."
            st.session_state.vector_store = create_vector_store()
            
            st.session_state.data_status = "Done! Chatbot ready."
            st.session_state.chatbot = AbleSupportChatbot(
                retriever=st.session_state.vector_store.as_retriever(search_kwargs={"k": 3})
            )
    
    if 'data_status' in st.session_state:
        st.write(st.session_state.data_status)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for chatbot
if "chatbot" not in st.session_state:
    # Check if we have vectorstore and processed data
    if os.path.exists("data/vector_store.pkl"):
        # Load existing vector store
        vector_store = create_vector_store()
        st.session_state.vector_store = vector_store
        st.session_state.chatbot = AbleSupportChatbot(
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )
    else:
        # Use fallback data for first-time use
        get_fallback_data()
        process_scraped_data()
        vector_store = create_vector_store()
        st.session_state.vector_store = vector_store
        st.session_state.chatbot = AbleSupportChatbot(
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )

# Main chat interface
st.title("Able Support Chatbot")
st.markdown("Ask me anything about Able, the digital product agency!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about Able?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show thinking animation
        thinking_msgs = ["Thinking.", "Thinking..", "Thinking..."]
        for i in range(3):
            message_placeholder.markdown(thinking_msgs[i])
            time.sleep(0.3)
        
        # Get response from chatbot
        response = st.session_state.chatbot.get_response(prompt)
        
        # Display response with typing effect
        full_response = ""
        for chunk in response.split():
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.05)
        
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add initial greeting if no messages yet
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("👋 Hi there! I'm the Able support chatbot. How can I help you today? You can ask me questions about Able's services, teams, mission, and more.")

# Footer
st.markdown("---")
st.caption("Able Support Chatbot powered by Streamlit and OpenAI")
