import json
import os
from typing import List, Dict, Any

class Document:
    """Simple document class to mimic LangChain's Document structure"""
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class TextSplitter:
    """Simple text splitter that splits by character count"""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately chunk_size with overlap"""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the chunk
            end = min(start + self.chunk_size, len(text))
            
            # Try to end at a period, question mark, or exclamation point
            if end < len(text):
                # Look for natural boundaries within the last 100 characters
                for i in range(end, max(start, end - 100), -1):
                    if text[i-1] in ['.', '!', '?', '\n']:
                        end = i
                        break
            
            # Add the chunk to our list
            chunks.append(text[start:end])
            
            # Move the start pointer, accounting for overlap
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        split_docs = []
        
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for text in texts:
                split_docs.append(Document(
                    page_content=text,
                    metadata=doc.metadata.copy()
                ))
        
        return split_docs

def process_scraped_data(source_file: str = 'data/scraped_data.json', 
                         fallback_file: str = 'data/fallback_data.json',
                         output_file: str = 'data/processed_data.json'):
    """
    Process the scraped data (or fallback data) into chunks suitable for
    embedding and retrieval.
    """
    print("Processing scraped data...")
    
    # Determine which data file to use
    data_file = source_file if os.path.exists(source_file) else fallback_file
    
    # Load data
    try:
        with open(data_file, 'r') as f:
            raw_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        return []
    
    # Convert raw data into documents
    documents = []
    
    for section_name, section_data in raw_data.items():
        # Process headings
        if 'headings' in section_data:
            headings_text = " ".join(section_data['headings'])
            if headings_text:
                documents.append(Document(
                    page_content=headings_text,
                    metadata={
                        "source": section_data.get('url', section_name),
                        "section": section_name,
                        "type": "headings"
                    }
                ))
        
        # Process paragraphs
        if 'paragraphs' in section_data:
            for i, paragraph in enumerate(section_data['paragraphs']):
                if paragraph:
                    documents.append(Document(
                        page_content=paragraph,
                        metadata={
                            "source": section_data.get('url', section_name),
                            "section": section_name,
                            "type": "paragraph",
                            "index": i
                        }
                    ))
    
    # Split documents into chunks
    text_splitter = TextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Convert to serializable format
    processed_data = [
        {
            "content": chunk.page_content,
            "metadata": chunk.metadata
        }
        for chunk in chunks
    ]
    
    # Save processed data
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print(f"Processing completed. {len(chunks)} chunks created.")
    print(f"Processed data saved to {output_file}")
    
    return processed_data

if __name__ == "__main__":
    process_scraped_data()
