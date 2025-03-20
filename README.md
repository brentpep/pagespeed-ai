# PageSpeed AI

A tool for analyzing website performance using Google Lighthouse and providing AI-powered optimization recommendations.

## Prerequisites

- Python 3.7+
- Node.js and npm (for Lighthouse)
- Chrome or Brave browser

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

The tool can now automatically extract critical CSS for above-the-fold content:

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

If no URL is provided, it will default to "https://example.com".

## Output

The tool will:
1. Run a Lighthouse analysis
2. Extract DOM structure and resources
3. Generate performance optimization recommendations
4. Create an implementation guide
5. Save results to `pagespeed_optimization_report.json`

## Features

- Performance analysis using Lighthouse
- Critical issue identification
- Prioritized optimization recommendations
- Implementation guide with code examples
- (Prototype) Automated image optimization

## Limitations

- Lighthouse may still require Chrome to be installed, even when specifying Brave as the browser
- If neither Chrome nor Brave is available, the tool will use mock data to demonstrate functionality
- Some features like image optimization and CSS extraction are basic prototypes
