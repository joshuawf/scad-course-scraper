# How to Use the SCAD Course Scraper

## Quick Start in Google Colab

1. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

2. **Install Requirements**: Run this in the first cell:
```python
!pip install requests pandas beautifulsoup4 lxml

3. Import the Scraper: Run this in the next cell:

pythonimport requests
exec(requests.get('https://raw.githubusercontent.com/joshuawf/scad-course-scraper/main/scad_scraper.py').text)

4. Run the Scraper:

python# Get all SCAD courses
df = scrape_all_courses()

5. Download Results:

pythonfrom google.colab import files
files.download('scad_courses.csv')

Test Single Subject
python# Test with one subject first
test_courses = test_single_subject('ACT')

Features

✅ Scrapes all SCAD course subjects
✅ Fixes encoding issues (Molière, résumé, etc.)
✅ Saves as UTF-8 CSV
✅ Two columns: Course Name & Description
✅ Respectful delays between requests
