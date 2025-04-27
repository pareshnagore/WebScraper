import scrapy
from urllib.parse import urljoin
from ..items import WebscraperItem, ContentBlock
from collections import defaultdict
import re

class WebsiteSpider(scrapy.Spider):
    name = 'website'
    max_depth = 5
    
    def __init__(self, url=None, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.base_url = "https://huggingface.co/learn/agents-course/"
        self.visited = set()  # Track visited URLs
        
        # Pre-defined navigation structure matching exact course order
        self.unit_structure = {
            'unit0': {
                'title': 'WELCOME TO THE COURSE',
                'type': 'main',
                'sections': [
                    {'path': 'introduction', 'title': 'Welcome to the course 👋'},
                    {'path': 'discord101', 'title': 'Discord 101', 'optional': True},
                    {'path': 'onboarding', 'title': 'Onboarding', 'optional': True}
                ]
            },
            'unit1': {
                'title': 'INTRODUCTION TO AGENTS',
                'type': 'main',
                'sections': [
                    {'path': 'introduction', 'title': 'Introduction'},
                    {'path': 'quiz1', 'title': 'Quick Quiz 1', 'is_quiz': True},
                    {'path': 'what-are-llms', 'title': 'What are LLMs?'},
                    {'path': 'messages-and-special-tokens', 'title': 'Messages and Special Tokens'},
                    {'path': 'tools', 'title': 'What are Tools?'},
                    {'path': 'quiz2', 'title': 'Quick Quiz 2', 'is_quiz': True},
                    {'path': 'agent-steps-and-structure', 'title': 'Understanding AI Agents through the Thought-Action-Observation Cycle'},
                    {'path': 'thoughts', 'title': 'Thoughts: Internal Reasoning and the Be-An-AgentPlus'},
                    {'path': 'actions', 'title': 'Actions: Enabling the Agent to Engage with its Environment'},
                    {'path': 'observations', 'title': 'Observe: Integrating Feedback to Reflect and Adapt'},
                    {'path': 'dummy-agent-library', 'title': 'Dummy Agent Library'},
                    {'path': 'tutorial', 'title': "Let's Create Our First Agent Using smokeagents"},
                    {'path': 'final-quiz', 'title': 'Unit 1 Final Quiz', 'is_quiz': True},
                    {'path': 'conclusion', 'title': 'Conclusion', 'is_conclusion': True}
                ]
            },
            'unit2': {
                'title': 'FRAMEWORKS FOR AI AGENTS',
                'type': 'main',
                'sections': [
                    {'path': 'introduction', 'title': 'Frameworks for AI Agents'},
                    # Unit 2.1
                    {'path': 'smolagents/introduction', 'title': 'Introduction to smokeagents', 'section': '2.1'},
                    {'path': 'smolagents/why_use_smolagents', 'title': 'Why use SmokeAgents?', 'section': '2.1'},
                    {'path': 'smolagents/quiz1', 'title': 'Quick Quiz 1', 'is_quiz': True, 'section': '2.1'},
                    {'path': 'smolagents/code_agents', 'title': 'Building Agents That Use Code', 'section': '2.1'},
                    {'path': 'smolagents/tool_calling_agents', 'title': 'Writing actions as code snippets or JSON blobs', 'section': '2.1'},
                    {'path': 'smolagents/tools', 'title': 'Tools', 'section': '2.1'},
                    {'path': 'smolagents/retrieval_agents', 'title': 'Retrieval Agents', 'section': '2.1'},
                    {'path': 'smolagents/quiz2', 'title': 'Quick Quiz 2', 'is_quiz': True, 'section': '2.1'},
                    {'path': 'smolagents/multi_agent_systems', 'title': 'Multi-Agent Systems', 'section': '2.1'},
                    {'path': 'smolagents/vision_agents', 'title': 'Vision and Browser agents', 'section': '2.1'},
                    {'path': 'smolagents/final_quiz', 'title': 'Final Quiz', 'is_quiz': True, 'section': '2.1'},
                    {'path': 'smolagents/conclusion', 'title': 'Conclusion', 'is_conclusion': True, 'section': '2.1'},
                    # Unit 2.2
                    {'path': 'llama-index/introduction', 'title': 'Introduction to LlamaIndex', 'section': '2.2'},
                    {'path': 'llama-index/llama-hub', 'title': 'Introduction to LlamaHub', 'section': '2.2'},
                    {'path': 'llama-index/components', 'title': 'What are Components in LlamaIndex?', 'section': '2.2'},
                    {'path': 'llama-index/tools', 'title': 'Using Tools in LlamaIndex', 'section': '2.2'},
                    {'path': 'llama-index/quiz1', 'title': 'Quick Quiz 1', 'is_quiz': True, 'section': '2.2'},
                    {'path': 'llama-index/agents', 'title': 'Using Agents in LlamaIndex', 'section': '2.2'},
                    {'path': 'llama-index/workflows', 'title': 'Creating Agents Workflows in LlamaIndex', 'section': '2.2'},
                    {'path': 'llama-index/quiz2', 'title': 'Quick Quiz 2', 'is_quiz': True, 'section': '2.2'},
                    {'path': 'llama-index/conclusion', 'title': 'Conclusion', 'is_conclusion': True, 'section': '2.2'},
                    # Unit 2.3
                    {'path': 'langgraph/introduction', 'title': 'Introduction to LangGraph', 'section': '2.3'},
                    {'path': 'langgraph/when_to_use_langgraph', 'title': 'What is LangGraph?', 'section': '2.3'},
                    {'path': 'langgraph/building_blocks', 'title': 'Building Blocks of LangGraph', 'section': '2.3'},
                    {'path': 'langgraph/first_graph', 'title': 'Building Your First LangGraph', 'section': '2.3'},
                    {'path': 'langgraph/document_analysis_agent', 'title': 'Document Analysis Graph', 'section': '2.3'},
                    {'path': 'langgraph/quiz1', 'title': 'Quick Quiz 1', 'is_quiz': True, 'section': '2.3'},
                    {'path': 'langgraph/conclusion', 'title': 'Conclusion', 'is_conclusion': True, 'section': '2.3'}
                ]
            },
            'unit3': {
                'title': 'USE CASE FOR AGENTS: RAG',
                'type': 'main',
                'sections': [
                    {'path': 'agentic-rag/introduction', 'title': 'Introduction to Use Case for Agents: RAG'},
                    {'path': 'agentic-rag/agentic-rag', 'title': 'Agentic Retrieval Augmented Generation (RAG)'},
                    {'path': 'agentic-rag/invitees', 'title': 'Creating a RAG Tool for Guest Stories'},
                    {'path': 'agentic-rag/tools', 'title': 'Building and Integrating Tools for Your Agent'},
                    {'path': 'agentic-rag/agent', 'title': 'Creating Your Own Agent'},
                    {'path': 'agentic-rag/conclusion', 'title': 'Conclusion', 'is_conclusion': True}
                ]
            },
            'unit4': {
                'title': 'FINAL PROJECT - CREATE, TEST, AND CERTIFY YOUR AGENT',
                'type': 'main',
                'sections': [
                    {'path': 'introduction', 'title': 'Introduction to Final Test'},
                    {'path': 'what-is-gaia', 'title': 'What is GAIA?'},
                    {'path': 'hands-on', 'title': 'The Final Hands-On'},
                    {'path': 'get-your-certificate', 'title': 'Get Your Certificate Of Excellence'},
                    {'path': 'conclusion', 'title': 'Conclusion of the Course', 'is_conclusion': True},
                    {'path': 'additional-readings', 'title': 'What Should You Learn Next!'}
                ]
            },
            'bonus-unit1': {
                'title': 'FINE-TUNING AN LLM FOR FUNCTION CALLING',
                'type': 'bonus',
                'sections': [
                    {'path': 'introduction', 'title': 'Introduction'},
                    {'path': 'what-is-function-calling', 'title': 'What is Function Calling?'},
                    {'path': 'fine-tuning', 'title': "Let's Fine Tune your model for Function calling"},
                    {'path': 'conclusion', 'title': 'Conclusion', 'is_conclusion': True}
                ]
            },
            'bonus-unit2': {
                'title': 'AGENT OBSERVABILITY AND EVALUATION',
                'type': 'bonus',
                'sections': [
                    {'path': 'introduction', 'title': 'Introduction'},
                    {'path': 'observability', 'title': 'What is agent observability and evaluation?'},
                    {'path': 'monitoring', 'title': 'Monitoring and evaluating agents'},
                    {'path': 'quiz', 'title': 'Quiz', 'is_quiz': True}
                ]
            },
            'bonus-unit3': {
                'title': 'AGENTS VS GAMES WITH POKEMON',
                'type': 'bonus',
                'sections': [
                    {'path': 'introduction', 'title': 'Introduction'},
                    {'path': 'state-of-art', 'title': 'The State of the Art in Using LLM in Games'},
                    {'path': 'from-llm-to-agents', 'title': 'From LLMs to AI Agents'},
                    {'path': 'building_your_pokemon_agent', 'title': 'Build Your Own Pokemon Battle Agent'},
                    {'path': 'launching_agent_battle', 'title': 'Launching Your Pokemon Battle Agent'},
                    {'path': 'conclusion', 'title': 'Conclusion', 'is_conclusion': True}
                ]
            }
        }
        
    def safe_extract_text(self, element, selector='::text', join_texts=True):
        """Safely extract text from an element"""
        texts = element.css(selector).getall()
        if not texts:
            return ''
        return ' '.join(t.strip() for t in texts) if join_texts else texts

    def extract_content_blocks(self, response):
        blocks = []
        
        # Extract main content area
        main_content = response.css('main')
        if not main_content:
            main_content = response.css('article')
        if not main_content:
            main_content = response.css('body')  # Fallback to body if no main/article
        
        if main_content:
            # Process headings
            for heading_level in range(1, 7):
                for heading in main_content.css(f'h{heading_level}'):
                    text = self.safe_extract_text(heading)
                    if text:
                        block = ContentBlock(
                            type='heading',
                            content=text,
                            level=heading_level
                        )
                        blocks.append(block)
                    
                    # Get content until next heading
                    next_elements = heading.xpath('./following-sibling::*')
                    for element in next_elements:
                        if element.css('h1, h2, h3, h4, h5, h6'):
                            break
                            
                        # Process paragraphs
                        if element.root.tag == 'p':
                            text = self.safe_extract_text(element)
                            if text:
                                block = ContentBlock(
                                    type='paragraph',
                                    content=text
                                )
                                blocks.append(block)
                            
                        # Process code blocks
                        elif element.root.tag == 'pre' or element.css('.highlight'):
                            code_content = element.css('code ::text').getall()
                            if code_content:
                                block = ContentBlock(
                                    type='code',
                                    content='\n'.join(line.strip() for line in code_content),
                                    language=element.css('[class*="language-"]::attr(class)').re_first(r'language-(\w+)') or 'text'
                                )
                                blocks.append(block)
                                
                        # Process lists
                        elif element.root.tag in ['ul', 'ol']:
                            items = []
                            for item in element.css('li'):
                                text = self.safe_extract_text(item)
                                if text:
                                    items.append(text)
                            if items:
                                block = ContentBlock(
                                    type='list',
                                    items=items,
                                    level=1
                                )
                                blocks.append(block)
            
        return blocks
    
    def parse(self, response):
        if response.url in self.visited:
            return
        
        self.visited.add(response.url)
        
        # Extract unit and section info from URL
        unit_match = re.search(r'(bonus-)?unit(\d+)', response.url)
        if not unit_match or not response.url.startswith(self.base_url):
            return
            
        # Determine unit and section
        is_bonus = bool(unit_match.group(1))
        unit_num = unit_match.group(2)
        unit = f"{'bonus-' if is_bonus else ''}unit{unit_num}"
        
        # Extract section path
        path = response.url.split(unit + '/')[1].rstrip('/')
        
        # Find section info in unit structure
        if unit not in self.unit_structure:
            return
            
        # Find section info
        section_info = None
        for section in self.unit_structure[unit]['sections']:
            if section['path'] == path:
                section_info = section
                break
                
        if not section_info:
            return
            
        # Calculate global order
        global_order = 0
        for u, data in self.unit_structure.items():
            if u == unit:
                global_order += data['sections'].index(section_info)
                break
            global_order += len(data['sections'])
            
        # Create item with all metadata
        item = WebscraperItem()
        item['url'] = response.url
        item['title'] = section_info['title']
        item['content_blocks'] = self.extract_content_blocks(response)
        item['depth'] = 0
        item['parent_url'] = None
        item['unit'] = unit
        item['unit_order'] = self.unit_structure[unit]['sections'].index(section_info) + 1
        item['section_type'] = self.unit_structure[unit]['type']
        item['section_number'] = section_info.get('section', '')
        item['is_optional'] = section_info.get('optional', False)
        item['is_quiz'] = section_info.get('is_quiz', False)
        item['is_conclusion'] = section_info.get('is_conclusion', False)
        item['lesson_type'] = 'Quiz' if item['is_quiz'] else 'Conclusion' if item['is_conclusion'] else 'Introduction' if 'introduction' in path.lower() else 'Content'
        item['global_order'] = global_order
        
        yield item
        
        # Find and queue next section
        current_index = self.unit_structure[unit]['sections'].index(section_info)
        if current_index + 1 < len(self.unit_structure[unit]['sections']):
            # Next section in same unit
            next_section = self.unit_structure[unit]['sections'][current_index + 1]
            next_url = f"{self.base_url}{unit}/{next_section['path']}"
            if next_url not in self.visited:
                yield scrapy.Request(next_url, callback=self.parse, priority=10)
        elif not is_bonus:
            # Try next main unit
            next_unit_num = int(unit_num) + 1
            next_unit = f"unit{next_unit_num}"
            if next_unit in self.unit_structure:
                first_section = self.unit_structure[next_unit]['sections'][0]
                next_url = f"{self.base_url}{next_unit}/{first_section['path']}"
                if next_url not in self.visited:
                    yield scrapy.Request(next_url, callback=self.parse, priority=5)
                    
        # Also collect other course links with lower priority
        for href in response.css('a::attr(href)').getall():
            url = urljoin(response.url, href)
            if url.startswith(self.base_url) and url not in self.visited:
                yield scrapy.Request(url, callback=self.parse, priority=0)