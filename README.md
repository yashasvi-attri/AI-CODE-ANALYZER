# AI Static Code Analyzer
A web-based application for analyzing Python and C++ code using rule-based checks and optional AI-driven insights.


## Overview
This project provides a simple interface to evaluate source code for common issues and improvement opportunities. It combines lightweight static analysis with optional AI suggestions to help improve code quality and readability.
The application is designed to work even when AI services are unavailable by falling back to rule-based analysis.

## Features
* Detects long or poorly formatted lines
* Basic syntax validation for Python code
* Language detection (Python / C++)
* AI-based suggestions (when API key is available)
* Improved code generation (AI-assisted)
* File upload support (.py, .cpp)
* Downloadable analysis report
* Graceful fallback to demo mode when AI is unavailable

## Tech Stack
* Python
* Streamlit
* OpenAI API

## Project Structure

```
app.py              # Main application file
requirements.txt    # Dependencies
README.md           # Project documentation
```

## How to Run Locally
1. Clone or download the repository
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   
   ```
   streamlit run app.py
   ```

## Usage
1. Paste code into the input box or upload a file
2. Click "Analyze Code"
3. View:
   * Rule-based checks
   * Issues found
   * Suggestions
   * Improved code

## Notes
* AI features require a valid OpenAI API key and available quota
* Without an API key, the app runs in demo mode using rule-based checks
* Large inputs are restricted to maintain performance

## Author
Yashasvi Attri
