# PageSpeed AI for Cursor Pro

A zero-configuration tool for analyzing website performance using Google Lighthouse and providing AI-powered optimization recommendations. Designed specifically for Cursor Pro users, this tool requires no API keys or external service accounts.

## Why PageSpeed AI for Cursor Pro?

- **No API Keys Required**: Works entirely with local tools and Cursor Pro's built-in AI capabilities
- **End-to-End Workflow**: Analyze sites with Lighthouse and generate optimization plans using Cursor Pro
- **Zero Configuration**: Just install the dependencies and start optimizing websites
- **Seamless Integration**: Results can be directly used with Cursor Pro's AI features

## Prerequisites

- Python 3.7+
- Node.js and npm (for Lighthouse)
- Chrome or Brave browser
- Cursor Pro (for AI-powered optimization plans)

## Installation

1. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv pagespeed_env
   source pagespeed_env/bin/activate  # On Windows: pagespeed_env\Scripts\activate
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Lighthouse globally:
   ```
   npm install -g lighthouse
   ```

4. Browser requirements:
   - The tool will attempt to use Brave browser if available when the `--use-brave` flag is used
   - If Brave cannot be used, or when using the `--use-chrome` flag, Chrome will be used
   - **Note:** Due to limitations in Lighthouse's browser detection, a working Chrome installation may still be required even when using Brave

## Usage

Run the tool with:
```
python pagespeed_optimizer.py [URL]
```

For example:
```
python pagespeed_optimizer.py https://example.com
```

By default, the tool uses Brave browser if it's installed. You can explicitly specify which browser to use with these flags:

```
# Force using Brave (default behavior)
python pagespeed_optimizer.py https://example.com --use-brave

# Force using Chrome instead of Brave
python pagespeed_optimizer.py https://example.com --use-chrome
```

### Extract Critical CSS

The tool can automatically extract critical CSS for above-the-fold content:

```
python pagespeed_optimizer.py https://example.com --extract-critical-css
```

This will:
1. Analyze the website as normal
2. Extract the CSS needed for above-the-fold content
3. Include the critical CSS in the JSON report
4. Save the critical CSS to a separate `critical.css` file

You can then use this critical CSS directly in your HTML by adding it to the `<head>` section:

```html
<head>
  <style>
    /* Paste the contents of critical.css here */
  </style>

  <!-- Then load the rest of your CSS asynchronously -->
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="styles.css"></noscript>
</head>
```

### Optimize and Test

The tool can create an optimized local version of a website and run comparative tests:

```
python pagespeed_optimizer.py https://example.com --optimize-and-test
```

This will:
1. Fetch the original website and download all resources (CSS, JS, images, fonts)
2. Create a local optimized version with best practices applied:
   - Inline critical CSS
   - Add defer/async attributes to scripts
   - Optimize images (WebP conversion, compression)
   - Add width/height attributes to images
   - Implement lazy loading for below-the-fold images
   - Add resource hints (preconnect, dns-prefetch)
   - Set cache control headers
3. Run Lighthouse tests on both original and optimized versions
4. Generate a comprehensive comparison report showing performance improvements

By default, all files will be saved to `implementation-tests/<domain>/`, where `<domain>` is extracted from the URL. You can also specify a custom output directory:

```
python pagespeed_optimizer.py https://example.com --optimize-and-test --output-dir=./my_optimized_site
```

The output includes:
- `implementation-tests/<domain>/index.html` - The optimized version of the website
- `implementation-tests/<domain>/comparison_report.html` - Visual HTML report comparing performance metrics
- `implementation-tests/<domain>/<domain>-optimization-results.md` - Markdown summary of improvements

This feature provides a proof-of-concept that demonstrates exactly how much your site could improve with the recommended optimizations.

If no URL is provided, it will default to "https://example.com".

## Output

The tool will:
1. Run a Lighthouse analysis
2. Extract DOM structure and resources
3. Generate performance optimization recommendations
4. Create an implementation guide
5. Save results to organized directories:
   - Analysis reports: `reports/<domain>/pagespeed_optimization_report.json`
   - Critical CSS: `reports/<domain>/critical.css`
   - Optimization tests: `implementation-tests/<domain>/`

This directory structure helps keep your analysis and implementation tests organized by domain.

## Using with Cursor Pro for AI-Powered Optimization Plans

The primary advantage of PageSpeed AI for Cursor Pro is the seamless integration with Cursor Pro's AI capabilities. You can generate comprehensive, actionable performance optimization plans directly within Cursor:

1. Run the PageSpeed AI tool on your target website:
   ```
   python pagespeed_optimizer.py https://yourwebsite.com --extract-critical-css
   ```

2. Use Cursor Pro to open the generated JSON report and critical CSS files.

3. Ask Cursor Pro to create an optimization plan with a prompt like:

   ```
   I've analyzed a website using PageSpeed AI. Based on the open files,
   please create a comprehensive "Actionable Performance Optimization Plan" that includes:

   1. A prioritized list of specific performance issues, ordered by impact
   2. Step-by-step instructions to fix each issue, with specific code examples
   3. Technical explanations for why each fix works
   4. An implementation timeline (quick wins vs. long-term improvements)
   5. Methods to measure the improvement after implementation

   Format the plan in Markdown with clear headings and code blocks. Focus on practical,
   actionable steps that can be implemented by developers.

   Additional context:
   - Website tech stack: [SPECIFY YOUR TECH STACK: e.g., WordPress, React, Vue, Angular, etc.]
   - Target audience: [SPECIFY WHO WILL IMPLEMENT: e.g., junior developers, senior team, yourself]
   - Hosting environment: [SPECIFY HOSTING: e.g., AWS, Netlify, shared hosting, etc.]
   - Priority areas: [SPECIFY ANY PARTICULAR FOCUS: e.g., mobile performance, SEO, Core Web Vitals]
   - Implementation timeframe: [SPECIFY URGENCY: e.g., immediate, next sprint, long-term project]
   ```

### Example

See the `results/Eversite.md` file in this repository for an example of a detailed performance optimization plan generated using this method.

### Including Critical CSS in Your Plan

If you've extracted critical CSS, Cursor Pro can provide more specific recommendations for CSS optimization, including exactly how to implement the critical CSS in your HTML and how to defer the loading of the remaining CSS.

## Features

- Performance analysis using Lighthouse
- Critical issue identification
- Prioritized optimization recommendations
- Implementation guide with code examples
- Critical CSS extraction for above-the-fold content
- Automatic optimization and comparative testing
- Visual performance improvement reports
- (Prototype) Automated image optimization

## Limitations

- Lighthouse may still require Chrome to be installed, even when specifying Brave as the browser
- If neither Chrome nor Brave is available, the tool will use mock data to demonstrate functionality
- Some features like image optimization and CSS extraction are basic prototypes
