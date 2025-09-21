```markdown
# SCAD Course Scraper 🎨📚

A Python scraper that extracts course information from the Savannah College of Art and Design (SCAD) course catalog and exports it to a clean CSV spreadsheet.

## What it does
- 🔍 Finds all course subjects (ACCE, ACT, ANIM, etc.)
- 📡 Uses SCAD's ribbit API to get course data
- 🧹 Cleans up encoding issues (fixes Molière, résumé, etc.)
- 📊 Creates a 2-column CSV: Course Name & Description
- 💾 Saves with proper UTF-8 encoding

## Quick Start
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joshuawf/scad-course-scraper/blob/main/SCAD_Scraper_Notebook.ipynb)

Or see [HOW_TO_USE.md](HOW_TO_USE.md) for detailed instructions.

## Sample Output
| Course Number and Name | Course Description |
|------------------------|-------------------|
| ACT 445 Auditioning for Careers in Classical Theater | This course is designed to give students interested in a career in classical theater audition preparation... |
| ACCE 110 Sewing Technology for Accessory Design | This course introduces students to the industry practices involved in producing accessories... |

## Requirements
- Python 3.6+
- requests
- pandas
- beautifulsoup4
- lxml

## Installation
```bash
pip install -r requirements.txt
python scad_scraper.py

Notes

⏱️ Takes ~5-10 minutes to scrape all courses
🌐 Respectful 1-second delays between requests
📝 Handles 50+ course subjects
🔧 Built for beginners with detailed error messages


Built for educational purposes. Please respect SCAD's website and terms of service.
