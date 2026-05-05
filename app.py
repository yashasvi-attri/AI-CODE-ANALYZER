import ast
import os
from typing import Dict, List, Optional

import streamlit as st
from openai import OpenAI


# ------------------ UTIL FUNCTIONS ------------------

def detect_language(code: str) -> str:
    lowered = code.lower()
    cpp_markers = ["#include", "std::", "int main(", "cout <<", "cin >>", "{", "}"]
    if any(marker in lowered for marker in cpp_markers):
        return "C++"
    return "Python"


def check_long_lines(code: str, max_length: int = 100) -> List[str]:
    warnings = []
    for index, line in enumerate(code.splitlines(), start=1):
        if len(line) > max_length:
            warnings.append(
                f"Line {index} is very long ({len(line)} chars). Keep under {max_length} chars."
            )
    return warnings


def check_python_syntax(code: str) -> Optional[str]:
    try:
        ast.parse(code)
        return None
    except SyntaxError as exc:
        return f"Python syntax issue near line {exc.lineno}: {exc.msg}"


def clean_ai_code(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        parts = code.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    return code


# ------------------ AI + FALLBACK ------------------

def call_openai_analysis(code: str, language: str) -> Dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")

    client = OpenAI(api_key=api_key)

    prompt = f"""
Analyze this {language} code.

Return exactly:

Issues Found:
...

Suggestions:
...

Improved Code:
...

Code:
{code}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )

    text = response.output_text.strip()

    return {
        "Issues Found": text,
        "Suggestions": text,
        "Improved Code": text,
    }


def build_demo_fallback(code: str, language: str, issues: List[str], reason: str):
    return {
        "Issues Found": "Demo mode: AI unavailable",
        "Suggestions": "Use better naming, optimize logic, check syntax",
        "Improved Code": code,
    }


# ------------------ MAIN LOGIC ------------------

def analyze_code(code: str) -> Dict[str, object]:
    result = {
        "rule_issues": [],
        "issues_found": "",
        "suggestions": "",
        "improved_code": "",
        "error": "",
        "ai_unavailable": False,
        "language": "",
    }

    if not code.strip():
        result["error"] = "Input is empty"
        return result

    if len(code) > 5000:
        result["error"] = "Code too long (limit 5000 chars)"
        return result

    language = detect_language(code)
    result["language"] = language

    issues = check_long_lines(code)

    if language == "Python":
        syntax = check_python_syntax(code)
        if syntax:
            issues.append(syntax)

    result["rule_issues"] = issues

    try:
        ai = call_openai_analysis(code, language)

        improved = clean_ai_code(ai.get("Improved Code", ""))

        if language == "Python":
            try:
                ast.parse(improved)
            except:
                improved = "AI returned invalid Python code."

        result["issues_found"] = ai.get("Issues Found", "")
        result["suggestions"] = ai.get("Suggestions", "")
        result["improved_code"] = improved

    except Exception as e:
        demo = build_demo_fallback(code, language, issues, str(e))
        result.update({
            "issues_found": demo["Issues Found"],
            "suggestions": demo["Suggestions"],
            "improved_code": demo["Improved Code"],
            "ai_unavailable": True
        })

    return result


# ------------------ UI ------------------

def show_home():
    st.markdown("""
    <h1 style='text-align: center; font-size: 42px;'>AI Static Code Analyzer</h1>
    <p style='text-align: center; font-size: 18px; color: gray;'>
    Analyze Python and C++ code using rule-based checks and AI-powered insights
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<h3>Features</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h4>Fast Analysis</h4>", unsafe_allow_html=True)
        st.write("Detect syntax errors and bad coding practices instantly.")

    with col2:
        st.markdown("<h4>AI Suggestions</h4>", unsafe_allow_html=True)
        st.write("Get intelligent improvements and optimized code output.")

    with col3:
        st.markdown("<h4>Clean Code</h4>", unsafe_allow_html=True)
        st.write("Improve readability and maintainability of your code.")

    st.markdown("---")

    st.markdown("<h3>How It Works</h3>", unsafe_allow_html=True)
    st.write("1. Paste or upload your code")
    st.write("2. Click Analyze")
    st.write("3. Get instant feedback")

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Analyzing", use_container_width=True):
            st.session_state.page = "analyzer"
            st.rerun()

    st.markdown("---")

    st.markdown(
        "<p style='text-align: center; color: gray;'>Built by Yashasvi Attri</p>",
        unsafe_allow_html=True
    )


def show_analyzer():
    if st.button("Back"):
        st.session_state.page = "home"

    st.title("Code Analyzer")

    uploaded = st.file_uploader("Upload file", type=["py", "cpp"])
    code_input = ""

    if uploaded:
        code_input = uploaded.read().decode("utf-8")
    else:
        code_input = st.text_area("Code Input", height=250)

    if st.button("Analyze Code"):
        result = analyze_code(code_input)

        if result["error"]:
            st.error(result["error"])
            return

        if result["ai_unavailable"]:
            st.warning("Demo Mode")
        else:
            st.success("AI Mode")

        st.subheader("Rule-Based Checks")
        if result["rule_issues"]:
            for i in result["rule_issues"]:
                st.warning(i)
        else:
            st.success("No issues")

        st.subheader("Issues Found")
        st.write(result["issues_found"])

        st.subheader("Suggestions")
        st.write(result["suggestions"])

        st.subheader("Improved Code")
        st.code(result["improved_code"])

        st.download_button(
            "Download Report",
            result["suggestions"],
            file_name="report.txt"
        )


# ------------------ MAIN ------------------

def main():
    st.set_page_config(
        page_title="AI Static Code Analyzer",
        layout="wide"
    )

    # Remove anchor icons completely
    st.markdown("""
    <style>
    a[href^="#"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        show_home()
    else:
        show_analyzer()


if __name__ == "__main__":
    main()