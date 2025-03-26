# Able Support Chatbot

A simple chatbot that answers frequently asked questions about Able, powered by LangChain and OpenAI's API.

## Overview

This chatbot uses web scraping to gather information about Able from their website, processes that data, and uses LangChain with OpenAI's API to generate accurate responses to user queries about the company.

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

This step scrapes Able’s website, processes the text, and builds semantic vector embeddings.

### 4. Run the scraper to collect data (if needed):
```
python -m src.scraper
python -m src.data_processor
python -m src.embeddings
```

## 🚀 Launch the Chatbot

### 5. Start the Streamlit app:
```bash
streamlit run app.py
```

Open your browser and go to:  
**http://localhost:8501**

---

## 💬 Using the Chatbot

- Type your question into the chat input field  
- The chatbot responds using LLM-based answers backed by scraped context from Able’s website  
- If no API key is detected, it will fallback to basic keyword-based responses  

---

## ✨ What the Bot Can Answer

- What Able does  
- Teams, services, and industries served  
- Company mission, values, and methodology  
- Technologies, location, and contact details  

---

## 🧱 Technical Features

- Web scraping with BeautifulSoup  
- LangChain + OpenAI API (GPT-3.5)  
- Custom vector store + retriever for semantic search  
- Modular architecture (retriever, embeddings, LLM interface, Streamlit UI)  
- Graceful fallback response system  
- Persistent chat history and conversational memory  

---

## 📦 CLI Tip

To launch the app quickly:
```bash
echo "To run the Able Support Chatbot, use the command: streamlit run app.py"
```

## 🧱 Project Structure

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

## 📹 Demo Video

[👉 Watch the 3-minute walkthrough here](link)

## Author

**Efe Eryildiz**  
[GitHub](https://github.com/EfeEryildiz) • [LinkedIn](https://linkedin.com/in/efe-e-44962715b)
