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

## Generating Actionable Performance Optimization Plans

You can use the output from PageSpeed AI to generate comprehensive, actionable performance optimization plans with the help of AI. Here's how:

1. Run the PageSpeed AI tool on your target website:
   ```
   python pagespeed_optimizer.py https://yourwebsite.com --extract-critical-css
   ```

2. Pass the generated JSON report to an AI model (such as ChatGPT or Claude) with the following prompt:

   ```
   I've analyzed a website using PageSpeed AI and need a detailed performance optimization plan.
   Here's the JSON data from the analysis:

   [PASTE THE CONTENTS OF pagespeed_optimization_report.json HERE]

   I've also extracted critical CSS for the site:

   [PASTE THE CONTENTS OF critical.css HERE]

   Please create a comprehensive "Actionable Performance Optimization Plan" that includes:

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

3. Save the AI-generated plan to a Markdown file (e.g., `optimization_plan.md`) for reference or sharing with your development team.

For best results:
- Include specific details about your tech stack in the prompt
- Ask for explanations tailored to your team's expertise level
- Request code examples in your specific programming languages/frameworks

### Example

See the `Eversite.md` file in this repository for an example of a detailed performance optimization plan generated using this method.

### Including Critical CSS in Your Plan

If you've extracted critical CSS using the `--extract-critical-css` flag, include it in your AI prompt for a more complete optimization plan:

```
I've analyzed a website using PageSpeed AI and need a detailed performance optimization plan.
Here's the JSON data from the analysis:

[PASTE THE CONTENTS OF pagespeed_optimization_report.json HERE]

I've also extracted critical CSS for the site:

[PASTE THE CONTENTS OF critical.css HERE]

Please create a comprehensive "Actionable Performance Optimization Plan" that includes:
...
```

This will allow the AI to provide more specific recommendations for CSS optimization, including exactly how to implement the critical CSS in your HTML and how to defer the loading of the remaining CSS.

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
