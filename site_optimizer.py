import os
import requests
import shutil
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PIL import Image
import io
import re
import time
from lighthouse import Lighthouse
from critical_css_extractor import extract_critical_css

class SiteOptimizer:
    """
    Creates an optimized local version of a website and runs comparative tests.

    This class handles extracting resources from a website, applying various
    performance optimizations, creating a local optimized version, and running
    comparative Lighthouse tests.
    """
    def __init__(self, url, output_dir="./optimized_site"):
        """
        Initialize the site optimizer.

        Args:
            url: The original website URL
            output_dir: Directory where the optimized site will be created
        """
        self.url = url
        self.output_dir = output_dir
        self.original_html = None
        self.dom = None
        self.resources = {
            "css": [],
            "js": [],
            "images": [],
            "fonts": []
        }
        self.optimized_resources = {
            "css": {},
            "js": {},
            "images": {},
            "fonts": {}
        }
        self.original_score = None
        self.optimized_score = None
        self.applied_optimizations = []

        # Create output directory structure
        self._create_directory_structure()

    def _create_directory_structure(self):
        """Create the necessary directory structure for the optimized site."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

        os.makedirs(self.output_dir)
        os.makedirs(os.path.join(self.output_dir, "css"))
        os.makedirs(os.path.join(self.output_dir, "js"))
        os.makedirs(os.path.join(self.output_dir, "images"))
        os.makedirs(os.path.join(self.output_dir, "fonts"))

    def fetch_original_site(self):
        """Fetch the original website HTML and extract its DOM structure."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            self.original_html = response.text
            self.dom = BeautifulSoup(self.original_html, 'html.parser')
            return True
        except Exception as e:
            print(f"Error fetching original site: {e}")
            return False

    def extract_resources(self):
        """Extract all resources (CSS, JS, images, fonts) from the website."""
        if not self.dom:
            self.fetch_original_site()

        # Extract CSS files
        css_links = self.dom.find_all('link', rel='stylesheet')
        for link in css_links:
            if 'href' in link.attrs:
                css_url = urljoin(self.url, link['href'])
                self.resources["css"].append({
                    "url": css_url,
                    "element": link
                })

        # Extract JS files
        scripts = self.dom.find_all('script', src=True)
        for script in scripts:
            js_url = urljoin(self.url, script['src'])
            self.resources["js"].append({
                "url": js_url,
                "element": script
            })

        # Extract images
        images = self.dom.find_all('img', src=True)
        for img in images:
            img_url = urljoin(self.url, img['src'])
            self.resources["images"].append({
                "url": img_url,
                "element": img
            })

        # Extract fonts
        font_links = self.dom.find_all('link', rel=lambda r: r and 'font' in r)
        for link in font_links:
            if 'href' in link.attrs:
                font_url = urljoin(self.url, link['href'])
                self.resources["fonts"].append({
                    "url": font_url,
                    "element": link
                })

        return self.resources

    def download_resources(self):
        """Download all extracted resources to the local directory."""
        for resource_type, resources in self.resources.items():
            for resource in resources:
                try:
                    response = requests.get(resource["url"])
                    if response.status_code == 200:
                        # Generate a filename based on the URL
                        parsed_url = urlparse(resource["url"])
                        filename = os.path.basename(parsed_url.path)
                        if not filename:
                            filename = f"resource_{hash(resource['url'])}"

                        # Save the resource
                        resource_path = os.path.join(self.output_dir, resource_type, filename)
                        with open(resource_path, 'wb') as f:
                            f.write(response.content)

                        # Store the local path for later use
                        resource["local_path"] = os.path.join(resource_type, filename)
                except Exception as e:
                    print(f"Error downloading {resource['url']}: {e}")

    def apply_optimizations(self):
        """Apply various optimizations to the resources."""
        # Apply specific optimizations
        self._optimize_css()
        self._optimize_js()
        self._optimize_images()
        self._optimize_html()

        return self.applied_optimizations

    def _optimize_css(self):
        """Apply CSS optimizations:
        1. Extract critical CSS
        2. Minify CSS
        3. Remove unused CSS rules
        """
        # Extract critical CSS
        try:
            critical_css = extract_critical_css(self.url)
            critical_css_path = os.path.join(self.output_dir, "css", "critical.css")
            with open(critical_css_path, 'w') as f:
                f.write(critical_css)

            # Add critical CSS to the optimized resources
            self.optimized_resources["css"]["critical"] = "css/critical.css"
            self.applied_optimizations.append("Extracted critical CSS for above-the-fold content")
        except Exception as e:
            print(f"Error extracting critical CSS: {e}")

        # TODO: Implement CSS minification
        # TODO: Implement unused CSS removal

    def _optimize_js(self):
        """Apply JavaScript optimizations:
        1. Add defer/async attributes to non-critical scripts
        2. Minify JavaScript
        """
        # Mark all scripts as deferred by default (will be handled in HTML optimization)
        self.applied_optimizations.append("Added defer attribute to non-critical scripts")

        # TODO: Implement JS minification

    def _optimize_images(self):
        """Apply image optimizations:
        1. Compress images
        2. Convert to WebP format
        3. Add explicit width/height attributes
        4. Add loading="lazy" for below-the-fold images
        """
        # Process each image
        for resource in self.resources["images"]:
            if "local_path" in resource:
                try:
                    img_path = os.path.join(self.output_dir, resource["local_path"])

                    # Open image
                    img = Image.open(img_path)

                    # Store original dimensions
                    width, height = img.size
                    resource["width"] = width
                    resource["height"] = height

                    # Compress and convert to WebP
                    webp_filename = os.path.splitext(os.path.basename(img_path))[0] + ".webp"
                    webp_path = os.path.join(self.output_dir, "images", webp_filename)

                    img.save(webp_path, format="WEBP", quality=85)

                    # Store WebP path
                    resource["webp_path"] = os.path.join("images", webp_filename)

                    # Check if this resulted in a smaller file
                    original_size = os.path.getsize(img_path)
                    webp_size = os.path.getsize(webp_path)

                    if webp_size < original_size:
                        resource["optimized_path"] = resource["webp_path"]
                        resource["savings"] = original_size - webp_size
                    else:
                        resource["optimized_path"] = resource["local_path"]
                        resource["savings"] = 0

                except Exception as e:
                    print(f"Error optimizing image {resource.get('url')}: {e}")

        self.applied_optimizations.append("Compressed and converted images to WebP format")
        self.applied_optimizations.append("Added explicit width/height attributes to images")
        self.applied_optimizations.append("Added lazy loading for below-the-fold images")

    def _optimize_html(self):
        """Apply HTML optimizations:
        1. Inline critical CSS
        2. Add defer attributes to scripts
        3. Add resource hints (preconnect, preload)
        4. Update image tags with width/height and loading attributes
        """
        if not self.dom:
            self.fetch_original_site()

        # Create a copy of the DOM for optimization
        optimized_dom = BeautifulSoup(str(self.dom), 'html.parser')

        # 1. Find or create head element
        head = optimized_dom.find('head')
        if not head:
            head = optimized_dom.new_tag('head')
            if optimized_dom.html:
                optimized_dom.html.insert(0, head)
            else:
                html = optimized_dom.new_tag('html')
                html.append(head)
                optimized_dom.append(html)

        # 2. Inline critical CSS
        if "critical" in self.optimized_resources["css"]:
            critical_css_path = os.path.join(self.output_dir, self.optimized_resources["css"]["critical"])
            with open(critical_css_path, 'r') as f:
                critical_css = f.read()

            # Create style tag with critical CSS
            style = optimized_dom.new_tag('style')
            style.string = critical_css
            head.insert(0, style)  # Insert at the beginning of head

        # 3. Update CSS links to load asynchronously
        css_links = optimized_dom.find_all('link', rel='stylesheet')
        for link in css_links:
            # Convert to preload
            link['rel'] = 'preload'
            link['as'] = 'style'
            link['onload'] = "this.onload=null;this.rel='stylesheet'"

            # Add local path reference if available
            for resource in self.resources["css"]:
                if resource.get("element") == link and "local_path" in resource:
                    link['href'] = resource["local_path"]

        # 4. Add noscript fallback for CSS
        for link in css_links:
            noscript = optimized_dom.new_tag('noscript')
            fallback_link = optimized_dom.new_tag('link')
            fallback_link['rel'] = 'stylesheet'
            fallback_link['href'] = link['href']
            noscript.append(fallback_link)
            link.insert_after(noscript)

        # 5. Add defer attribute to scripts
        scripts = optimized_dom.find_all('script', src=True)
        for script in scripts:
            # Don't defer scripts that are already async
            if 'async' not in script.attrs:
                script['defer'] = ""

            # Update to local path
            for resource in self.resources["js"]:
                if resource.get("element") == script and "local_path" in resource:
                    script['src'] = resource["local_path"]

        # 6. Optimize image tags
        images = optimized_dom.find_all('img', src=True)

        # Find all images to identify LCP candidate
        # Simple heuristic: largest image in the first viewport is likely the LCP
        viewport_height = 800  # Assume 800px is approximately the viewport height
        lcp_candidate = None
        largest_area = 0

        for img in images:
            # Calculate position (very rough estimation)
            # In a real implementation, this would use a headless browser
            parent = img.parent
            if not parent:
                continue

            # Assume images near the top are more likely to be in the viewport
            position = len(str(parent.find_previous_siblings()))

            # Find matching resource
            for resource in self.resources["images"]:
                if resource.get("element") == img and "local_path" in resource:
                    # Update src to local path
                    img['src'] = resource["local_path"]

                    # Add width and height if available
                    if "width" in resource and "height" in resource:
                        img['width'] = str(resource["width"])
                        img['height'] = str(resource["height"])

                        # Check if this is potentially the LCP
                        area = resource["width"] * resource["height"]
                        if position < viewport_height and area > largest_area:
                            largest_area = area
                            lcp_candidate = img

                    # Add WebP version in picture element if available
                    if "webp_path" in resource:
                        # Create picture element
                        picture = optimized_dom.new_tag('picture')
                        source = optimized_dom.new_tag('source')
                        source['srcset'] = resource["webp_path"]
                        source['type'] = 'image/webp'

                        # Get the parent node before extracting the img
                        parent_node = img.parent

                        # Extract img (this removes it from the DOM)
                        img_copy = img.extract()

                        # Add elements to picture
                        picture.append(source)
                        picture.append(img_copy)

                        # Insert picture where img was
                        if parent_node:
                            parent_node.append(picture)

                        # DO NOT try to replace img after extracting it
                        # img.replace_with(picture) - This line causes an error

        # Add fetchpriority="high" to LCP candidate
        if lcp_candidate:
            lcp_candidate['fetchpriority'] = 'high'

            # Preload LCP image
            lcp_src = lcp_candidate.get('src')
            if lcp_src:
                preload = optimized_dom.new_tag('link')
                preload['rel'] = 'preload'
                preload['href'] = lcp_src
                preload['as'] = 'image'
                head.insert(0, preload)

        # Add loading="lazy" to non-LCP images
        for img in images:
            if img != lcp_candidate:
                img['loading'] = 'lazy'

        # 7. Add resource hints for remaining external domains
        external_domains = set()

        # Extract domains from remaining external resources
        for resource_type, resources in self.resources.items():
            for resource in resources:
                parsed_url = urlparse(resource.get("url", ""))
                if parsed_url.netloc:
                    external_domains.add(parsed_url.netloc)

        # Add preconnect for each external domain
        for domain in external_domains:
            preconnect = optimized_dom.new_tag('link')
            preconnect['rel'] = 'preconnect'
            preconnect['href'] = f"https://{domain}"
            preconnect['crossorigin'] = ""
            head.insert(0, preconnect)

            dns_prefetch = optimized_dom.new_tag('link')
            dns_prefetch['rel'] = 'dns-prefetch'
            dns_prefetch['href'] = f"https://{domain}"
            head.insert(0, dns_prefetch)

        # 8. Create cache manifest
        cache_manifest = optimized_dom.new_tag('meta')
        cache_manifest['http-equiv'] = 'Cache-Control'
        cache_manifest['content'] = 'max-age=31536000'
        head.append(cache_manifest)

        # 9. Save optimized HTML
        with open(os.path.join(self.output_dir, 'index.html'), 'w') as f:
            f.write(str(optimized_dom))

        self.applied_optimizations.append("Inlined critical CSS in the head")
        self.applied_optimizations.append("Deferred loading of non-critical CSS")
        self.applied_optimizations.append("Added resource hints (preconnect, dns-prefetch)")
        self.applied_optimizations.append("Optimized LCP image loading with fetchpriority")
        self.applied_optimizations.append("Added cache control headers")

    def run_lighthouse_tests(self):
        """Run Lighthouse tests on both original and optimized versions."""
        # Initialize Lighthouse for original site
        lighthouse_original = Lighthouse()
        self.original_results = lighthouse_original.audit(self.url)
        self.original_score = self.original_results['categories']['performance']['score'] * 100

        print(f"Original site performance score: {self.original_score:.1f}")

        # Run Lighthouse on the optimized version
        # Use file:// protocol for local files
        optimized_url = f"file://{os.path.abspath(os.path.join(self.output_dir, 'index.html'))}"
        lighthouse_optimized = Lighthouse()

        # Wait a moment to ensure all resources are available
        time.sleep(2)

        self.optimized_results = lighthouse_optimized.audit(optimized_url)
        self.optimized_score = self.optimized_results['categories']['performance']['score'] * 100

        print(f"Optimized site performance score: {self.optimized_score:.1f}")

        return {
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvement": self.optimized_score - self.original_score
        }

    def generate_comparison_report(self):
        """Generate an HTML report comparing original and optimized versions."""
        # Extract domain for report title
        domain = urlparse(self.url).netloc
        if not domain:
            domain = "example-com"  # Default if URL parsing fails

        comparison = {
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvement": self.optimized_score - self.original_score,
            "original_metrics": {
                "fcp": self.original_results['audits']['first-contentful-paint']['displayValue'],
                "lcp": self.original_results['audits']['largest-contentful-paint']['displayValue'],
                "tbt": self.original_results['audits']['total-blocking-time']['displayValue'],
                "cls": self.original_results['audits']['cumulative-layout-shift']['displayValue']
            },
            "optimized_metrics": {
                "fcp": self.optimized_results['audits']['first-contentful-paint']['displayValue'],
                "lcp": self.optimized_results['audits']['largest-contentful-paint']['displayValue'],
                "tbt": self.optimized_results['audits']['total-blocking-time']['displayValue'],
                "cls": self.optimized_results['audits']['cumulative-layout-shift']['displayValue']
            },
            "applied_optimizations": self.applied_optimizations
        }

        # Create HTML report
        html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageSpeed AI - Optimization Report for {domain}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }}
        .scores-container {{
            display: flex;
            justify-content: space-around;
            margin: 2rem 0;
        }}
        .score-card {{
            text-align: center;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            width: 30%;
        }}
        .original {{
            background-color: #f8f9fa;
        }}
        .optimized {{
            background-color: #e3f2fd;
        }}
        .improvement {{
            background-color: #e8f5e9;
        }}
        .score {{
            font-size: 3rem;
            font-weight: bold;
        }}
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
        }}
        .metrics-table th, .metrics-table td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .metrics-table th {{
            background-color: #f5f5f5;
        }}
        .optimizations {{
            margin: 2rem 0;
        }}
        .optimization-item {{
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            background-color: #f9f9f9;
            border-left: 4px solid #4caf50;
        }}
        .cta {{
            text-align: center;
            margin: 2rem 0;
        }}
        .cta a {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #2196f3;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PageSpeed AI Optimization Report for {domain}</h1>
        <p>Comparing performance between original and optimized versions of <strong>{self.url}</strong></p>
        <p><small>Generated on {time.strftime('%Y-%m-%d at %H:%M:%S')}</small></p>
    </div>

    <div class="scores-container">
        <div class="score-card original">
            <h2>Original Score</h2>
            <div class="score">{comparison['original_score']:.1f}</div>
        </div>
        <div class="score-card optimized">
            <h2>Optimized Score</h2>
            <div class="score">{comparison['optimized_score']:.1f}</div>
        </div>
        <div class="score-card improvement">
            <h2>Improvement</h2>
            <div class="score">+{comparison['improvement']:.1f}</div>
        </div>
    </div>

    <h2>Core Web Vitals Comparison</h2>
    <table class="metrics-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Original</th>
                <th>Optimized</th>
                <th>Improvement</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>First Contentful Paint (FCP)</td>
                <td>{comparison['original_metrics']['fcp']}</td>
                <td>{comparison['optimized_metrics']['fcp']}</td>
                <td>{self._calculate_improvement(comparison['original_metrics']['fcp'], comparison['optimized_metrics']['fcp'])}</td>
            </tr>
            <tr>
                <td>Largest Contentful Paint (LCP)</td>
                <td>{comparison['original_metrics']['lcp']}</td>
                <td>{comparison['optimized_metrics']['lcp']}</td>
                <td>{self._calculate_improvement(comparison['original_metrics']['lcp'], comparison['optimized_metrics']['lcp'])}</td>
            </tr>
            <tr>
                <td>Total Blocking Time (TBT)</td>
                <td>{comparison['original_metrics']['tbt']}</td>
                <td>{comparison['optimized_metrics']['tbt']}</td>
                <td>{self._calculate_improvement(comparison['original_metrics']['tbt'], comparison['optimized_metrics']['tbt'])}</td>
            </tr>
            <tr>
                <td>Cumulative Layout Shift (CLS)</td>
                <td>{comparison['original_metrics']['cls']}</td>
                <td>{comparison['optimized_metrics']['cls']}</td>
                <td>{self._calculate_improvement(comparison['original_metrics']['cls'], comparison['optimized_metrics']['cls'], reverse=True)}</td>
            </tr>
        </tbody>
    </table>

    <div class="optimizations">
        <h2>Applied Optimizations</h2>
        {''.join([f'<div class="optimization-item">{opt}</div>' for opt in comparison['applied_optimizations']])}
    </div>

    <div class="cta">
        <a href="index.html" target="_blank">View Optimized Page</a>
    </div>

    <div class="footer">
        <p>Generated by PageSpeed AI &copy; {time.strftime('%Y')}</p>
    </div>
</body>
</html>"""

        # Save HTML report
        with open(os.path.join(self.output_dir, 'comparison_report.html'), 'w') as f:
            f.write(html_report)

        print(f"Comparison report saved to {os.path.join(self.output_dir, 'comparison_report.html')}")
        return comparison

    def _calculate_improvement(self, original, optimized, reverse=False):
        """Calculate and format the improvement between two metrics."""
        # Extract numbers from strings like "1.2 s" or "0.12"
        try:
            orig_num = float(re.search(r'([\d\.]+)', original).group(1))
            opt_num = float(re.search(r'([\d\.]+)', optimized).group(1))

            if reverse:  # For metrics where lower is better
                improvement = orig_num - opt_num
                if improvement > 0:
                    return f"⬇️ {improvement:.2f}"
                else:
                    return f"⬆️ {abs(improvement):.2f}"
            else:  # For metrics where higher is better
                improvement = opt_num - orig_num
                if improvement < 0:
                    return f"⬇️ {abs(improvement):.2f}"
                else:
                    return f"⬆️ {improvement:.2f}"
        except:
            return "N/A"

def optimize_and_test(url, output_dir="./optimized_site"):
    """
    Wrapper function to optimize a site and run comparative tests.

    Args:
        url: The URL of the website to optimize
        output_dir: Directory to save the optimized site

    Returns:
        Dictionary with comparison results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract domain for report
    domain = urlparse(url).netloc
    if not domain:
        domain = "example-com"  # Default if URL parsing fails

    optimizer = SiteOptimizer(url, output_dir)

    print("1. Fetching original site...")
    optimizer.fetch_original_site()

    print("2. Extracting resources...")
    optimizer.extract_resources()

    print("3. Downloading resources...")
    optimizer.download_resources()

    print("4. Applying optimizations...")
    optimizer.apply_optimizations()

    print("5. Running Lighthouse tests...")
    test_results = optimizer.run_lighthouse_tests()

    print("6. Generating comparison report...")
    comparison = optimizer.generate_comparison_report()

    # Save a summary markdown file with the results
    markdown_summary = f"""# Performance Optimization Results for {domain}

## Summary

- **URL Tested**: {url}
- **Date**: {time.strftime('%Y-%m-%d')}
- **Original Performance Score**: {comparison['original_score']:.1f}
- **Optimized Performance Score**: {comparison['optimized_score']:.1f}
- **Improvement**: +{comparison['improvement']:.1f} points

## Applied Optimizations

{chr(10).join(['- ' + opt for opt in comparison['applied_optimizations']])}

## Core Web Vitals Comparison

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| First Contentful Paint (FCP) | {comparison['original_metrics']['fcp']} | {comparison['optimized_metrics']['fcp']} | {optimizer._calculate_improvement(comparison['original_metrics']['fcp'], comparison['optimized_metrics']['fcp'])} |
| Largest Contentful Paint (LCP) | {comparison['original_metrics']['lcp']} | {comparison['optimized_metrics']['lcp']} | {optimizer._calculate_improvement(comparison['original_metrics']['lcp'], comparison['optimized_metrics']['lcp'])} |
| Total Blocking Time (TBT) | {comparison['original_metrics']['tbt']} | {comparison['optimized_metrics']['tbt']} | {optimizer._calculate_improvement(comparison['original_metrics']['tbt'], comparison['optimized_metrics']['tbt'])} |
| Cumulative Layout Shift (CLS) | {comparison['original_metrics']['cls']} | {comparison['optimized_metrics']['cls']} | {optimizer._calculate_improvement(comparison['original_metrics']['cls'], comparison['optimized_metrics']['cls'], reverse=True)} |

## Next Steps

1. Review the optimized implementation at `{os.path.join(output_dir, 'index.html')}`
2. View the detailed comparison report at `{os.path.join(output_dir, 'comparison_report.html')}`
3. Consider implementing these optimizations on your production site
"""

    # Save markdown summary
    with open(os.path.join(output_dir, f"{domain}-optimization-results.md"), 'w') as f:
        f.write(markdown_summary)

    print("\n✨ Performance Improvement Summary ✨")
    print(f"Original Score: {comparison['original_score']:.1f}")
    print(f"Optimized Score: {comparison['optimized_score']:.1f}")
    print(f"Improvement: +{comparison['improvement']:.1f} points")

    print("\nOptimizations applied:")
    for opt in comparison['applied_optimizations']:
        print(f"- {opt}")

    print(f"\nDetailed report saved to '{os.path.join(output_dir, 'comparison_report.html')}'")
    print(f"Optimized site available at '{os.path.join(output_dir, 'index.html')}'")
    print(f"Markdown summary saved to '{os.path.join(output_dir, f'{domain}-optimization-results.md')}'")

    return comparison
