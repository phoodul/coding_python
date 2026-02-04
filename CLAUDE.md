# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A multi-project Python repository containing:

- **gopython-main/** — The primary project: a 15-chapter practical Python textbook ("혼자 만들면서 공부하는 파이썬"). Each chapter is a self-contained mini-project built step-by-step (e.g. `step_2_1.py` → `step_2_2.py` → …). Each chapter has its own `README.md` with package install instructions.
- **duty_manager/** — A PyQt6 hospital duty roster management app. Multiple historical versions exist (`duty_manager_v9.7.py` … `duty_manager_final.py`). The latest is `duty_manager_final.py` (v4.1).
- **LAI_scheduler/** — A Tkinter GUI for scheduling long-acting injectable medications. Latest version is `lai_scheduler_v3.py`.
- **seegene/** — Selenium-based web automation for a medical lab system, with Kakaotalk notification integration. Latest is `seegene_auto.py` (note: contains unresolved merge conflict markers).
- **KOREA_IT_academy/** — Classroom exercises and Baekjoon Online Judge problem solutions.
- **drd2/** — Diablo 2-related utility scripts.

## Environment & Python Version

- **Recommended Python**: 3.12.x (required for ch_05 EasyOCR; most other chapters also work on 3.13.x)
- **OS**: Windows
- **IDE**: PyCharm (`.idea/` present) and VS Code both used
- There is **no single root `requirements.txt`**. Dependencies are per-chapter/per-project; install commands are in each chapter's `README.md`.

## Running Code

There is no centralized build, lint, or test runner for the repository. Each chapter and project is run individually:

```bash
# Run a specific gopython chapter step
python gopython-main/ch_01/step_2_3.py

# Run the duty manager (latest)
python duty_manager/duty_manager_final.py

# Run the LAI scheduler (latest)
python LAI_scheduler/lai_scheduler_v3.py

# Run the seegene automation
python seegene/seegene_auto.py
```

## Linting / Formatting

The only configured tool is **isort** (import sorting), configured in [gopython-main/pyproject.toml](gopython-main/pyproject.toml) with the `black` profile. No black, flake8, pylint, or mypy is configured.

```bash
# Sort imports for a file (from gopython-main/)
isort ch_01/step_2_3.py
```

## gopython-main Architecture

Each chapter (`ch_01`–`ch_15`) is an independent mini-project. Files within a chapter follow a strict step progression — later steps build on earlier ones and should be run in order. Key patterns:

| Chapter | What it builds | Key libs |
|---------|---------------|----------|
| ch_01 | Folder size measurement + chart | pathlib, matplotlib, NumPy |
| ch_02 | Card spending analysis | pandas, openpyxl, seaborn |
| ch_03 | Furniture layout visualization | Pillow, geometry math |
| ch_04 | QR code contact cards | qrcode, vobject |
| ch_05 / ch_05_paddleocr | Image OCR + translation | EasyOCR or PaddleOCR, DeepL, Streamlit |
| ch_06 | Shopping trend scraping | Playwright |
| ch_07 | Market-cap analysis | Playwright, Plotly, pandas |
| ch_08 | Keyword competition analysis | Streamlit |
| ch_09 | Stock price alert bot | schedule, email |
| ch_10 | News article crawler | BeautifulSoup, newspaper3k |
| ch_11 | TTS reading app | google-cloud-texttospeech, Streamlit |
| ch_12 | E-commerce product crawler | Playwright |
| ch_13 | AI news translation | Ollama (local LLM), Streamlit |
| ch_14_genai | English dictation app | google-genai (Gemini API), Streamlit |

**Preferred folders for updated chapters:**
- Chapter 5: use `ch_05_paddleocr/` (PaddleOCR) unless EasyOCR is specifically needed
- Chapter 14: use `ch_14_genai/` (new Google Gemini API package `google-genai`)

## Known Gotchas

- **ch_04**: Pin versions with `pip install "pillow==10.4.0" "qrcode==7.4.2"` to avoid a `ValueError` in newer qrcode releases.
- **ch_07**: Pin versions with `pip install "plotly<6" "kaleido<1"` for correct chart export.
- **ch_13**: Model name changed — use `gemma3:4b` or `gemma3:12b` (not the older `gemma2:9b`).
- **ch_14**: Package renamed from `google-generativeai` to `google-genai`; API usage changed significantly.
- **Playwright Inspector** (ch_06, ch_07, ch_12): If Inspector generates JavaScript instead of Python, set Target → Python → Pytest/Library in the Inspector window.
- **seegene/seegene_auto.py**: Contains unresolved git merge conflict markers — resolve before running.
- **ch_01**: Before running `step_2_4.py`, edit the JSON output of `step_2_3.py` to remove cloud-synced folders (OneDrive, Google Drive, etc.) or execution will be very slow.
