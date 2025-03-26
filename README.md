# Able Support Chatbot

A simple chatbot that answers frequently asked questions about Able, powered by LangChain and OpenAI's API.

## Overview

This chatbot uses web scraping to gather information about Able from their website, processes that data, and uses LangChain with OpenAI's API to generate accurate responses to user queries about the company.

## Features

- Web scraping of Able's website for up-to-date information
- Vector embeddings for semantic search and context retrieval
- OpenAI API integration for natural language processing
- Streamlit-based user interface for easy interaction
- Conversational memory to maintain context

## 🔧 Setup Instructions
### Ensure you have:
- Python 3.8 or higher installed
- An OpenAI API key

### 1. Clone this repository 

### 2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
### 3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 🧠 Prepare the Knowledge Base

### 4. Run the scraper to collect data (if needed):
   ```
   python -m src.scraper
   python -m src.data_processor
   python -m src.embeddings
   ```
### 5. Launch the application:
   ```
   streamlit run app.py
   ```

## Project Structure

- `data/`: Contains raw and processed data from Able's website
- `src/`: Source code for the chatbot functionality
  - `scraper.py`: Web scraping functionality
  - `data_processor.py`: Data processing and preparation
  - `embeddings.py`: Vector embedding creation and management
  - `retriever.py`: Context retrieval logic
  - `llm_interface.py`: OpenAI API interaction
  - `chatbot.py`: Core chatbot logic
- `app.py`: Streamlit application
- `requirements.txt`: Project dependencies

## Sample Questions

- "What does Able do?"
- "What kinds of teams does Able have?"
- "What industries has Able worked with?"
- "What is Able's mission?"
- "Where is Able located?"

## Demo Video

[👉 Watch the 3-minute walkthrough here](link)

## Author

**Efe Eryildiz**  
[GitHub](https://github.com/EfeEryildiz) • [LinkedIn](https://linkedin.com/in/efe-e-44962715b)
