from selenium import webdriver
from lighthouse import Lighthouse
import requests
from bs4 import BeautifulSoup
import json
import os
from PIL import Image
import io
import sys
import argparse
from critical_css_extractor import extract_critical_css
from site_optimizer import optimize_and_test
from urllib.parse import urlparse

class WebsitePerformanceAnalyzer:
    def __init__(self, url, use_brave=True):
        self.url = url
        self.use_brave = use_brave
        self.lighthouse_results = None
        self.dom_elements = None
        self.resources = []
        self.critical_issues = []

    def run_lighthouse_analysis(self):
        """Run Lighthouse analysis and store results"""
        # Initialize Lighthouse
        lighthouse = Lighthouse(use_brave=self.use_brave)
        self.lighthouse_results = lighthouse.audit(self.url)

        return self.lighthouse_results

    def extract_dom_structure(self):
        """Extract DOM structure for analysis"""
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.dom_elements = soup
        return soup

    def extract_resources(self):
        """Extract and analyze resource loading"""
        # This would extract JS, CSS, images, fonts, etc.
        if not self.dom_elements:
            self.extract_dom_structure()

        # Extract scripts
        scripts = self.dom_elements.find_all('script', src=True)
        for script in scripts:
            self.resources.append({
                'type': 'script',
                'url': script['src'],
                'attributes': script.attrs
            })

        # Extract stylesheets
        styles = self.dom_elements.find_all('link', rel='stylesheet')
        for style in styles:
            self.resources.append({
                'type': 'stylesheet',
                'url': style['href'],
                'attributes': style.attrs
            })

        # Extract images
        images = self.dom_elements.find_all('img', src=True)
        for img in images:
            self.resources.append({
                'type': 'image',
                'url': img['src'],
                'attributes': img.attrs
            })

        return self.resources

    def analyze_performance(self):
        """Perform comprehensive performance analysis"""
        if not self.lighthouse_results:
            self.run_lighthouse_analysis()

        if not self.resources:
            self.extract_resources()

        # Analyze performance scores
        performance_score = self.lighthouse_results['categories']['performance']['score'] * 100

        # Extract key metrics
        fcp = self.lighthouse_results['audits']['first-contentful-paint']['displayValue']
        lcp = self.lighthouse_results['audits']['largest-contentful-paint']['displayValue']
        tbt = self.lighthouse_results['audits']['total-blocking-time']['displayValue']
        cls = self.lighthouse_results['audits']['cumulative-layout-shift']['displayValue']

        # Generate critical issues list
        for audit_id, audit in self.lighthouse_results['audits'].items():
            if audit['score'] is not None and audit['score'] < 0.9 and 'details' in audit:
                self.critical_issues.append({
                    'id': audit_id,
                    'title': audit['title'],
                    'description': audit['description'],
                    'score': audit['score'],
                    'details': audit.get('details', {})
                })

        return {
            'performance_score': performance_score,
            'key_metrics': {
                'first_contentful_paint': fcp,
                'largest_contentful_paint': lcp,
                'total_blocking_time': tbt,
                'cumulative_layout_shift': cls
            },
            'critical_issues': sorted(self.critical_issues, key=lambda x: x['score'])
        }

class OptimizationRecommender:
    def __init__(self, analyzer_results, url=None):
        self.analyzer_results = analyzer_results
        self.url = url  # Store the URL for critical CSS extraction
        self.recommendations = []
        self.code_snippets = {}
        self.critical_css = None

    def generate_recommendations(self):
        """Generate specific optimization recommendations"""
        issues = self.analyzer_results['critical_issues']

        for issue in issues:
            recommendation = {
                'issue': issue['title'],
                'importance': 'high' if issue['score'] < 0.5 else 'medium',
                'steps': [],
                'code_changes': []
            }

            # Generate specific recommendations based on issue type
            if issue['id'] == 'render-blocking-resources':
                recommendation['steps'].append('Add defer attribute to non-critical JavaScript')
                recommendation['steps'].append('Inline critical CSS and defer non-critical CSS')
                recommendation['code_changes'].append({
                    'file_type': 'html',
                    'description': 'Add defer to script tags',
                    'example': '<script src="non-critical.js" defer></script>'
                })

            elif issue['id'] == 'unminified-css' or issue['id'] == 'unminified-javascript':
                recommendation['steps'].append(f"Minify {issue['id'].split('-')[1].upper()} files")
                recommendation['steps'].append('Set up build process with minification tools')

            elif issue['id'] == 'unused-css-rules':
                recommendation['steps'].append('Remove unused CSS')
                recommendation['steps'].append('Consider using PurgeCSS to automatically remove unused styles')

            elif issue['id'] == 'unused-javascript':
                recommendation['steps'].append('Implement code splitting')
                recommendation['steps'].append('Remove dead code')

            elif issue['id'] == 'offscreen-images':
                recommendation['steps'].append('Implement lazy loading for images')
                recommendation['code_changes'].append({
                    'file_type': 'html',
                    'description': 'Add loading="lazy" to image tags',
                    'example': '<img src="image.jpg" loading="lazy" alt="Description">'
                })

            elif issue['id'] == 'uses-responsive-images':
                recommendation['steps'].append('Use responsive image syntax with srcset')
                recommendation['code_changes'].append({
                    'file_type': 'html',
                    'description': 'Implement srcset for responsive images',
                    'example': '<img srcset="small.jpg 300w, medium.jpg 600w, large.jpg 1200w" sizes="(max-width: 320px) 280px, (max-width: 640px) 580px, 1200px" src="fallback.jpg" alt="Description">'
                })

            elif issue['id'] == 'uses-optimized-images':
                recommendation['steps'].append('Compress images and use modern formats like WebP')
                recommendation['steps'].append('Set up an image optimization build step')

            elif issue['id'] == 'uses-text-compression':
                recommendation['steps'].append('Enable GZIP or Brotli compression on your server')
                recommendation['code_changes'].append({
                    'file_type': 'server',
                    'description': 'Apache: Enable GZIP compression',
                    'example': '''<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript
</IfModule>'''
                })

            # Add more issue types as needed
            else:
                recommendation['steps'].append(f'Address {issue["title"]}')
                recommendation['steps'].append('Refer to Lighthouse documentation for specifics')

            self.recommendations.append(recommendation)

        return self.recommendations

    def extract_critical_css(self):
        """Extract critical CSS for the analyzed URL."""
        if not self.url:
            return "/* Critical CSS extraction requires a URL */"

        try:
            print(f"Extracting critical CSS for {self.url}...")
            self.critical_css = extract_critical_css(self.url)
            return self.critical_css
        except Exception as e:
            print(f"Error extracting critical CSS: {e}")
            return f"/* Error extracting critical CSS: {e} */"

    def get_critical_css(self):
        """Get the critical CSS, extracting it if not already done."""
        if self.critical_css is None:
            self.extract_critical_css()
        return self.critical_css

    def generate_implementation_guide(self):
        """Generate step-by-step implementation guide"""
        if not self.recommendations:
            self.generate_recommendations()

        implementation_guide = {
            'summary': f"Found {len(self.recommendations)} issues to address",
            'estimated_score_improvement': self._estimate_improvement(),
            'prioritized_tasks': [],
            'automation_opportunities': [],
            'critical_css': self.get_critical_css() if self.url else None
        }

        # Prioritize recommendations
        prioritized_recs = sorted(self.recommendations, key=lambda x: x['importance'] == 'high', reverse=True)

        for i, rec in enumerate(prioritized_recs):
            implementation_guide['prioritized_tasks'].append({
                'priority': i + 1,
                'task': rec['issue'],
                'steps': rec['steps'],
                'code_examples': rec['code_changes']
            })

        # Identify automation opportunities
        if any(r['issue'] == 'uses-optimized-images' for r in self.recommendations):
            implementation_guide['automation_opportunities'].append({
                'task': 'Image optimization',
                'automation_tool': 'Build an automated image optimization pipeline',
                'implementation_complexity': 'Medium'
            })

        if any(r['issue'] == 'unminified-css' or r['issue'] == 'unminified-javascript' for r in self.recommendations):
            implementation_guide['automation_opportunities'].append({
                'task': 'Asset minification',
                'automation_tool': 'Implement webpack/gulp build process',
                'implementation_complexity': 'Low'
            })

        return implementation_guide

    def _estimate_improvement(self):
        """Estimate potential score improvement"""
        current_score = self.analyzer_results['performance_score']

        # Simple heuristic algorithm
        potential_improvement = 0
        for issue in self.analyzer_results['critical_issues']:
            if issue['score'] < 0.5:
                potential_improvement += (0.9 - issue['score']) * 5
            else:
                potential_improvement += (0.9 - issue['score']) * 2

        # Cap the maximum improvement
        potential_improvement = min(potential_improvement, 100 - current_score)

        return {
            'current_score': current_score,
            'potential_score': min(current_score + potential_improvement, 100),
            'percentage_improvement': f"{potential_improvement:.1f}%"
        }

class AutomatedOptimizer:
    def __init__(self, url, analyzer, recommender):
        self.url = url
        self.analyzer = analyzer
        self.recommender = recommender

    def optimize_images(self, image_urls):
        """Automatically optimize images"""
        optimized_images = []

        for img_url in image_urls:
            try:
                # Download image
                response = requests.get(img_url)
                img = Image.open(io.BytesIO(response.content))

                # Optimize image
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=85, optimize=True)

                optimized_images.append({
                    'original_url': img_url,
                    'optimized_data': output.getvalue(),
                    'original_size': len(response.content),
                    'optimized_size': output.tell(),
                    'savings_percentage': round((1 - output.tell() / len(response.content)) * 100, 1)
                })
            except Exception as e:
                print(f"Failed to optimize {img_url}: {e}")

        return optimized_images

    def generate_critical_css(self, html, css_urls):
        """Extract critical CSS for above-the-fold content"""
        # This would be implemented using a CSS extraction tool
        # For now, we'll return a placeholder
        return "/* Critical CSS would be extracted here */"

    def minify_resources(self, js_content, css_content):
        """Minify JS and CSS resources"""
        # This would be implemented using minification libraries
        # For now, we'll return placeholders
        return {
            'js_minified': "/* JS would be minified here */",
            'css_minified': "/* CSS would be minified here */"
        }

def main():
    parser = argparse.ArgumentParser(description='Analyze website performance using Lighthouse')
    parser.add_argument('url', nargs='?', default="https://example.com",
                        help='URL of the website to analyze (default: https://example.com)')
    parser.add_argument('--use-brave', action='store_true', default=True,
                        help='Use Brave browser instead of Chrome (default: True)')
    parser.add_argument('--use-chrome', dest='use_brave', action='store_false',
                        help='Use Chrome browser instead of Brave')
    parser.add_argument('--extract-critical-css', action='store_true',
                        help='Extract critical CSS for the analyzed URL')
    parser.add_argument('--optimize-and-test', action='store_true',
                        help='Create an optimized local version and run comparative tests')
    parser.add_argument('--output-dir', default=None,
                        help='Directory to save the optimized site (default: ./implementation-tests/<domain>)')
    args = parser.parse_args()

    url = args.url
    use_brave = args.use_brave
    extract_critical = args.extract_critical_css

    # Extract domain name from URL for organizing outputs
    domain = urlparse(url).netloc
    if not domain:
        domain = "example-com"  # Default if URL parsing fails

    # Create reports directory if it doesn't exist
    reports_dir = os.path.join("reports", domain)
    os.makedirs(reports_dir, exist_ok=True)

    # Set output directory for optimization tests
    if args.output_dir:
        output_dir = args.output_dir
    else:
        implementation_tests_dir = os.path.join("implementation-tests", domain)
        output_dir = implementation_tests_dir

    # If optimize-and-test flag is set, run that workflow
    if args.optimize_and_test:
        print(f"Starting optimization and testing of {url}...")
        # Create implementation-tests directory if it doesn't exist
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        optimize_and_test(url, output_dir)
        return

    print(f"Analyzing {url}...")
    print(f"Using {'Brave' if use_brave else 'Chrome'} browser...")

    try:
        # Initialize analyzer
        analyzer = WebsitePerformanceAnalyzer(url, use_brave=use_brave)

        # Run analysis
        print("Running Lighthouse analysis...")
        analysis_results = analyzer.analyze_performance()

        # Generate recommendations
        print("Generating optimization recommendations...")
        recommender = OptimizationRecommender(analysis_results, url=url if extract_critical else None)
        recommendations = recommender.generate_recommendations()
        implementation_guide = recommender.generate_implementation_guide()

        # Extract critical CSS if requested
        if extract_critical:
            print("Critical CSS extracted and included in the report")

        # Initialize optimizer for automated fixes
        optimizer = AutomatedOptimizer(url, analyzer, recommender)

        # Generate report
        report = {
            'url': url,
            'analysis': analysis_results,
            'recommendations': recommendations,
            'implementation_guide': implementation_guide
        }

        # Output report to domain-specific directory
        report_file = os.path.join(reports_dir, 'pagespeed_optimization_report.json')
        print("Saving report...")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Analysis complete. Current score: {analysis_results['performance_score']}")
        print(f"Potential improvement: {implementation_guide['estimated_score_improvement']['percentage_improvement']}")
        print(f"Report saved to {report_file}")

        # Save critical CSS to the reports directory if extracted
        if extract_critical and recommender.critical_css:
            css_file = os.path.join(reports_dir, 'critical.css')
            with open(css_file, 'w') as f:
                f.write(recommender.critical_css)
            print(f"Critical CSS saved to {css_file}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
