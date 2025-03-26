import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_able_website():
    """
    Scrapes the Able website for information about the company,
    services, teams, industries, and locations.
    """
    print("Starting to scrape Able's website...")
    
    # URLs to scrape - add more as needed
    urls = [
        "https://able.co/",
        "https://able.co/about",
        "https://able.co/services",
        "https://able.co/careers",
        "https://able.co/contact",
    ]
    
    all_data = {}
    
    for url in urls:
        print(f"Scraping {url}...")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page title
            title = soup.title.string if soup.title else url.split('/')[-1]
            
            # Extract page content - this is a simple approach
            # In a real implementation, you'd want to target specific sections based on HTML structure
            paragraphs = soup.find_all('p')
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            # Store data by URL/section for organization
            page_name = url.split('/')[-1] if url.split('/')[-1] else "home"
            all_data[page_name] = {
                "title": title,
                "url": url,
                "headings": [h.get_text(strip=True) for h in headings if h.get_text(strip=True)],
                "paragraphs": [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            }
            
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save raw scraped data
    with open('data/scraped_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Scraping completed. Data saved to data/scraped_data.json")
    return all_data

# Hard-coded data about Able in case scraping fails or for testing
def get_fallback_data():
    """
    Returns hard-coded information about Able as a fallback
    in case web scraping fails or for testing purposes.
    """
    fallback_data = {
        "about": {
            "title": "About Able - Digital Product Agency",
            "url": "https://able.co/about",
            "headings": ["About Able", "Our Mission", "Our Values", "Our Teams"],
            "paragraphs": [
                "Able is a full-service digital product agency that partners with funded startups and established brands to build innovative, user-focused products.",
                "Our mission is to help organizations transform their ideas into exceptional digital products that create value for users and drive business growth.",
                "We bring together talent across product management, design, and engineering to deliver world-class digital products.",
                "Our teams collaborate with clients as true partners, guiding them through every stage of the product development lifecycle.",
                "We're headquartered in New York City, with team members across the United States and globally."
            ]
        },
        "services": {
            "title": "Services - Able Digital Product Agency",
            "url": "https://able.co/services",
            "headings": ["Our Services", "Product Strategy", "Design", "Engineering", "Growth"],
            "paragraphs": [
                "Able provides end-to-end digital product services, from strategy and discovery through design, development, and growth.",
                "Our product strategy team helps clients validate ideas, identify opportunities, and create roadmaps for success.",
                "Our design team creates intuitive, accessible, and engaging user experiences across web and mobile platforms.",
                "Our engineering team builds scalable, robust applications using modern technologies and best practices.",
                "We work across various industries including fintech, healthcare, education, media, and enterprise software."
            ]
        },
        "teams": {
            "title": "Teams at Able",
            "paragraphs": [
                "Able has multidisciplinary teams across several key areas: Product Management, Design, Engineering, and Strategy.",
                "Our Product teams guide product development from concept to launch, ensuring alignment with business goals and user needs.",
                "Our Design teams create intuitive, engaging user experiences and interfaces that bring products to life.",
                "Our Engineering teams build robust, scalable applications using various technologies including React, React Native, Node.js, Python, and more.",
                "Our Strategy teams help clients validate ideas, identify opportunities, and create roadmaps for successful products."
            ]
        },
        "industries": {
            "title": "Industries We Serve",
            "paragraphs": [
                "Able works across a diverse range of industries including fintech, healthcare, education, media, retail, and enterprise software.",
                "In fintech, we've built payment platforms, investment tools, and financial management applications.",
                "For healthcare clients, we've created patient portals, telemedicine solutions, and health management systems.",
                "Our education work includes learning management systems, educational content platforms, and administrative tools.",
                "We've also worked with media companies on content delivery platforms, subscription services, and audience engagement tools."
            ]
        },
        "locations": {
            "title": "Able Locations",
            "paragraphs": [
                "Able is headquartered in New York City.",
                "We have team members distributed across the United States and globally.",
                "Our global presence allows us to work with clients around the world and build diverse teams with varied perspectives."
            ]
        }
    }
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save fallback data
    with open('data/fallback_data.json', 'w') as f:
        json.dump(fallback_data, f, indent=2)
    
    print("Fallback data saved to data/fallback_data.json")
    return fallback_data

if __name__ == "__main__":
    try:
        # Try web scraping first
        scraped_data = scrape_able_website()
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Using fallback data instead.")
        # Use fallback data if scraping fails
        scraped_data = get_fallback_data()
