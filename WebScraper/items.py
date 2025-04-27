import scrapy

class ContentBlock(scrapy.Item):
    type = scrapy.Field()  # heading, paragraph, list, code, table
    content = scrapy.Field()
    level = scrapy.Field()  # For headings (h1, h2, etc.) or list nesting
    language = scrapy.Field()  # For code blocks
    items = scrapy.Field()  # For list items
    parent = scrapy.Field()  # For nested structures

class WebscraperItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content_blocks = scrapy.Field()  # List of ContentBlock items
    depth = scrapy.Field()
    parent_url = scrapy.Field()
    
    # Course structure fields
    unit = scrapy.Field()  # e.g., "unit0", "unit1", "bonus-unit1"
    unit_order = scrapy.Field()  # Order within the unit
    section_type = scrapy.Field()  # "main" or "bonus"
    section_number = scrapy.Field()  # e.g., "2.1", "2.2" for sub-sections
    is_optional = scrapy.Field()  # Boolean for optional sections
    is_quiz = scrapy.Field()  # Boolean to identify quiz items
    is_conclusion = scrapy.Field()  # Boolean to mark conclusion sections
    lesson_type = scrapy.Field()  # e.g., "Introduction", "Exercise", "Quiz"
    global_order = scrapy.Field()  # Overall order in the course
