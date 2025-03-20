import requests
from bs4 import BeautifulSoup
import re
import cssselect
from urllib.parse import urljoin

class CriticalCSSExtractor:
    def __init__(self, url, viewport_width=1200, viewport_height=800):
        """Initialize the critical CSS extractor.

        Args:
            url: The URL of the webpage to analyze
            viewport_width: The viewport width to consider for above-the-fold content
            viewport_height: The viewport height to consider for above-the-fold content
        """
        self.url = url
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.html = None
        self.dom = None
        self.css_files = []
        self.css_contents = {}
        self.critical_selectors = set()

    def fetch_page(self):
        """Fetch the webpage HTML."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            self.html = response.text
            self.dom = BeautifulSoup(self.html, 'html.parser')
            return True
        except Exception as e:
            print(f"Error fetching page: {e}")
            return False

    def extract_css_files(self):
        """Extract all CSS files referenced in the HTML."""
        if not self.dom:
            if not self.fetch_page():
                return False

        # Find all external CSS files
        css_links = self.dom.find_all('link', rel='stylesheet')
        for link in css_links:
            if 'href' in link.attrs:
                css_url = urljoin(self.url, link['href'])
                self.css_files.append(css_url)

        # Find all inline styles
        style_tags = self.dom.find_all('style')
        for i, style in enumerate(style_tags):
            if style.string:
                inline_key = f"inline-{i}"
                self.css_files.append(inline_key)
                self.css_contents[inline_key] = style.string

        return True

    def fetch_css_contents(self):
        """Fetch the contents of all external CSS files."""
        for css_url in self.css_files:
            # Skip inline styles that are already stored
            if css_url.startswith('inline-'):
                continue

            try:
                response = requests.get(css_url)
                response.raise_for_status()
                self.css_contents[css_url] = response.text
            except Exception as e:
                print(f"Error fetching CSS file {css_url}: {e}")

    def parse_css(self, css_content):
        """Parse CSS content and extract selectors."""
        # Regular expression to extract selectors from CSS
        # This is simplified and doesn't handle all edge cases
        selector_pattern = re.compile(r'([^{]+){[^}]*}')
        matches = selector_pattern.findall(css_content)

        selectors = []
        for match in matches:
            # Clean up selector (remove comments, whitespace)
            selector = match.strip()
            # Skip @media, @keyframes, etc.
            if selector.startswith('@'):
                continue
            # Split combined selectors
            for s in selector.split(','):
                selectors.append(s.strip())

        return selectors

    def find_above_fold_elements(self):
        """Find elements that are above the fold."""
        # In a real implementation, this would use a headless browser
        # to determine which elements are visible in the viewport.
        # For this simplified version, we'll consider all elements
        # in the first part of the document as "above the fold".

        # Get elements that are likely above the fold
        above_fold_elements = []

        # Header elements
        above_fold_elements.extend(self.dom.find_all(['header', 'nav']))

        # Hero sections or main banners (commonly above fold)
        hero_sections = self.dom.find_all(class_=lambda c: c and ('hero' in c.lower() or 'banner' in c.lower()))
        above_fold_elements.extend(hero_sections)

        # First few sections
        sections = self.dom.find_all(['section', 'div'], class_=lambda c: c and 'section' in c.lower())
        if sections:
            # Take the first few sections (likely above fold)
            above_fold_elements.extend(sections[:3])

        # LCP image (largest contentful paint)
        lcp_candidates = self.dom.find_all('img')
        if lcp_candidates:
            # Sort by size (if width/height attributes are present)
            sized_images = [img for img in lcp_candidates if img.has_attr('width') and img.has_attr('height')]
            if sized_images:
                sized_images.sort(key=lambda img: int(img['width']) * int(img['height']), reverse=True)
                above_fold_elements.append(sized_images[0])

        return above_fold_elements

    def extract_element_selectors(self, elements):
        """Extract CSS selectors that target the given elements."""
        selectors = set()

        for element in elements:
            # Add the element's tag
            selectors.add(element.name)

            # Add classes
            if element.has_attr('class'):
                for cls in element['class']:
                    selectors.add(f".{cls}")
                    selectors.add(f"{element.name}.{cls}")

            # Add ID
            if element.has_attr('id'):
                selectors.add(f"#{element['id']}")

            # Add parent-child relationships for better specificity
            parent = element.parent
            if parent and parent.name != '[document]':
                if parent.name:
                    selectors.add(f"{parent.name} {element.name}")

                    # Add with classes
                    if element.has_attr('class'):
                        for cls in element['class']:
                            selectors.add(f"{parent.name} .{cls}")

        return selectors

    def match_selectors(self, element_selectors, css_selectors):
        """Match element selectors with CSS selectors."""
        matching_selectors = set()

        for css_selector in css_selectors:
            # Remove pseudo-classes/elements for matching purposes
            base_selector = re.sub(r'::?[a-zA-Z-]+(\([^)]*\))?', '', css_selector)

            # Check if this CSS selector matches any of our element selectors
            for element_selector in element_selectors:
                if element_selector in base_selector:
                    matching_selectors.add(css_selector)
                    break

        return matching_selectors

    def extract_critical_css(self):
        """Extract critical CSS for above-the-fold content."""
        # Fetch the page if not already done
        if not self.dom:
            if not self.fetch_page():
                return ""

        # Extract CSS files if not already done
        if not self.css_files:
            self.extract_css_files()
            self.fetch_css_contents()

        # Find above-fold elements
        above_fold_elements = self.find_above_fold_elements()

        # Extract selectors for above-fold elements
        element_selectors = self.extract_element_selectors(above_fold_elements)

        # Parse all CSS and find matching selectors
        all_critical_selectors = set()

        for css_url, css_content in self.css_contents.items():
            # Parse CSS content to get selectors
            css_selectors = self.parse_css(css_content)

            # Match selectors
            matching_selectors = self.match_selectors(element_selectors, css_selectors)
            all_critical_selectors.update(matching_selectors)

        # Extract critical CSS rules
        critical_css = self.generate_critical_css(all_critical_selectors)

        return critical_css

    def generate_critical_css(self, critical_selectors):
        """Generate critical CSS from selected selectors."""
        critical_css = "/* Critical CSS extracted by PageSpeed AI */\n"

        # Common essential CSS properties that should always be included
        critical_css += """
html, body {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

*, *::before, *::after {
    box-sizing: inherit;
}
"""

        # Add CSS for selected critical selectors
        for css_url, css_content in self.css_contents.items():
            # Regular expression to extract selector and rules
            rule_pattern = re.compile(r'([^{]+){([^}]*)}')
            matches = rule_pattern.findall(css_content)

            for selector, rules in matches:
                selector = selector.strip()

                # Skip @media, @keyframes, etc.
                if selector.startswith('@'):
                    continue

                # Check if this selector is in our critical selectors
                selector_parts = [s.strip() for s in selector.split(',')]

                if any(s in critical_selectors for s in selector_parts):
                    critical_css += f"{selector} {{\n"

                    # Format rules nicely
                    rule_parts = [r.strip() for r in rules.split(';') if r.strip()]
                    for rule in rule_parts:
                        critical_css += f"    {rule};\n"

                    critical_css += "}\n\n"

        return critical_css


def extract_critical_css(url, viewport_width=1200, viewport_height=800):
    """Helper function to extract critical CSS from a URL."""
    extractor = CriticalCSSExtractor(url, viewport_width, viewport_height)
    return extractor.extract_critical_css()


if __name__ == "__main__":
    # Example usage
    url = "https://example.com"
    critical_css = extract_critical_css(url)
    print(critical_css)
