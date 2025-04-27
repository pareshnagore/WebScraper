
# WebScraper

A web scraper built with Scrapy to extract content from the Hugging Face Agents Course.

## Project Structure
```
WebScraper/
├── WebScraper/
│   ├── __init__.py
│   ├── items.py
│   ├── pipelines.py
│   ├── settings.py
│   └── spiders/
│       └── website_spider.py
├── requirements.txt
└── README.md
```

## Requirements
- Python 3.x
- Scrapy>=2.11.0
- reportlab>=4.0.8
- itemadapter>=0.8.0

## Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/WebScraper.git

# Navigate to project directory
cd WebScraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
# Run the spider
scrapy crawl website
```

## Output
The spider generates a PDF file containing the course content organized by units and sections.