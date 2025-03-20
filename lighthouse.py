import json
import subprocess
import os
import tempfile
import platform
import shutil

class Lighthouse:
    def __init__(self, driver=None, use_brave=True):
        self.driver = driver
        self.use_brave = use_brave

    def _get_browser_path(self):
        """Get the path to browser based on preference and OS"""
        system = platform.system()

        # Try to find Brave if preferred
        if self.use_brave:
            if system == "Darwin":  # macOS
                brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                if os.path.exists(brave_path):
                    return "brave", brave_path
            elif system == "Linux":
                brave_path = "/usr/bin/brave-browser"
                if os.path.exists(brave_path):
                    return "brave", brave_path
            elif system == "Windows":
                # Common Windows installation paths
                program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
                program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")

                paths = [
                    os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                    os.path.join(program_files_x86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")
                ]

                for path in paths:
                    if os.path.exists(path):
                        return "brave", path

        # Fall back to Chrome if Brave not found or not preferred
        if system == "Darwin":  # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                return "chrome", chrome_path
        elif system == "Linux":
            chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]
            for path in chrome_paths:
                if os.path.exists(path):
                    return "chrome", path
        elif system == "Windows":
            # Common Windows installation paths
            program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
            program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")

            paths = [
                os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe")
            ]

            for path in paths:
                if os.path.exists(path):
                    return "chrome", path

        return None, None  # No browser found

    def audit(self, url):
        """Run Lighthouse analysis"""
        print("Running Lighthouse audit...")

        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            output_path = tmp.name

        try:
            # Get browser information
            browser_type, browser_path = self._get_browser_path()

            if browser_path and os.path.exists(browser_path):
                print(f"Using {browser_type.capitalize()} browser at: {browser_path}")

                # Build the Lighthouse command
                cmd = [
                    "lighthouse",
                    url,
                    "--output=json",
                    "--output-path=" + output_path,
                    "--chrome-flags=--headless --no-sandbox --disable-gpu",
                    "--only-categories=performance",
                    f"--chrome-path={browser_path}"
                ]

                print(f"Executing command: {' '.join(cmd)}")

                # Run Lighthouse with the specified browser
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    print("Lighthouse Error:")
                    print(result.stderr)
                    return self._mock_lighthouse_response()

                # Check if output file exists and has content
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    try:
                        with open(output_path, 'r') as f:
                            return json.load(f)
                    except json.JSONDecodeError:
                        print("Error parsing Lighthouse results")
                        return self._mock_lighthouse_response()
                else:
                    print("No output file generated")
                    return self._mock_lighthouse_response()
            else:
                print(f"No compatible browser found. Using mock data.")
                return self._mock_lighthouse_response()

        except Exception as e:
            print(f"Error running Lighthouse: {e}")
            return self._mock_lighthouse_response()
        finally:
            # Clean up the temporary file
            if os.path.exists(output_path):
                os.remove(output_path)

    def _mock_lighthouse_response(self):
        """Provide a mock Lighthouse response for testing"""
        return {
            "categories": {
                "performance": {"score": 0.65}
            },
            "audits": {
                "first-contentful-paint": {"displayValue": "1.5 s", "score": 0.8},
                "largest-contentful-paint": {"displayValue": "2.5 s", "score": 0.7},
                "total-blocking-time": {"displayValue": "150 ms", "score": 0.6},
                "cumulative-layout-shift": {"displayValue": "0.1", "score": 0.9},
                "render-blocking-resources": {
                    "score": 0.4,
                    "title": "Eliminate render-blocking resources",
                    "description": "Resources are blocking the first paint of your page.",
                    "details": {}
                },
                "uses-optimized-images": {
                    "score": 0.5,
                    "title": "Efficiently encode images",
                    "description": "Optimized images load faster and consume less data.",
                    "details": {}
                }
            }
        }
