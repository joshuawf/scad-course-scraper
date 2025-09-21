import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import re
from bs4 import BeautifulSoup

def get_course_prefixes():
    """
    Get all course prefixes from SCAD catalog main page
    """
    url = "https://catalog.scad.edu/courses/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to course pages
        course_links = soup.find_all('a', href=re.compile(r'/courses/[a-zA-Z]+/'))
        
        prefixes = []
        for link in course_links:
            href = link.get('href')
            # Extract prefix from href like '/courses/acce/'
            match = re.search(r'/courses/([a-zA-Z]+)/', href)
            if match:
                prefix = match.group(1).upper()
                prefixes.append(prefix)
        
        # Remove duplicates and sort
        prefixes = sorted(list(set(prefixes)))
        
        print(f"Found {len(prefixes)} course prefixes")
        return prefixes
        
    except requests.RequestException as e:
        print(f"Error fetching course prefixes: {e}")
        return []

def get_course_data_xml(subject_code):
    """
    Get course data XML for a specific subject using the ribbit API
    """
    base_url = "https://catalog.scad.edu/ribbit/"
    params = {
        'page': 'getcourse.rjs',
        'subject': subject_code
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        print(f"  API call successful - {len(response.text)} characters")
        return response.text
        
    except requests.RequestException as e:
        print(f"  Error fetching XML for {subject_code}: {e}")
        return None

def parse_course_xml(xml_content):
    """
    Parse the XML content to extract course information
    Based on the actual SCAD XML structure observed
    """
    courses = []
    
    try:
        # Clean up the XML content
        xml_content = xml_content.strip()
        
        if not xml_content or not xml_content.startswith('<?xml'):
            print("  Response doesn't appear to be XML format")
            return courses
        
        root = ET.fromstring(xml_content)
        
        # Look for course elements based on observed structure
        course_elements = root.findall('.//course')
        
        print(f"  Found {len(course_elements)} course elements in XML")
        
        for course in course_elements:
            # Get course code from the 'code' attribute
            course_code = course.get('code', '').strip()
            
            if not course_code:
                continue
            
            # Get all text content from the course element
            # The course title and description are in the CDATA content
            course_content = ''.join(course.itertext()).strip()
            
            if course_content:
                # Parse the HTML content within the CDATA
                soup = BeautifulSoup(course_content, 'html.parser')
                
                # Extract course title - look for the course name in various elements
                title = ""
                
                # Try to find title in strong tags or spans with specific classes
                title_elem = soup.find('strong')
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    # Remove the course code from title if it's there
                    title = re.sub(rf'^{re.escape(course_code)}\s*', '', title_text).strip()
                
                # If no title found, try other methods
                if not title:
                    # Look for text after the course code
                    text_content = soup.get_text().strip()
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    if lines:
                        # First line often contains the title
                        first_line = lines[0]
                        title = re.sub(rf'^{re.escape(course_code)}\s*', '', first_line).strip()
                
                # Extract full description (everything)
                description = soup.get_text().strip()
                
                # Clean up description and fix encoding issues
                description = re.sub(r'\s+', ' ', description).strip()
                
                # Fix specific encoding problems that we identified
                encoding_fixes = [
                    ('MoliÃ¨re', 'Molière'),
                    ('Moli\xc3\xa8re', 'Molière'), 
                    ('Moliàère', 'Molière'),
                    ('rÃ©sumÃ©', 'résumé'),
                    ('r\xc3\xa9sum\xc3\xa9', 'résumé'),
                    ('réàsumé', 'résumé'),
                    # Add more common patterns
                    ('Ã¨', 'è'), ('Ã©', 'é'), ('Ã ', 'à'), ('Ã¡', 'á'), 
                    ('Ã¢', 'â'), ('Ã£', 'ã'), ('Ã¤', 'ä'), ('Ã¥', 'å'),
                    ('Ã§', 'ç'), ('Ãª', 'ê'), ('Ã«', 'ë'), ('Ã¬', 'ì'),
                    ('Ã­', 'í'), ('Ã®', 'î'), ('Ã¯', 'ï'), ('Ã±', 'ñ'),
                    ('Ã²', 'ò'), ('Ã³', 'ó'), ('Ã´', 'ô'), ('Ã¶', 'ö'),
                    ('Ã¹', 'ù'), ('Ãº', 'ú'), ('Ã»', 'û'), ('Ã¼', 'ü'),
                    ('â€™', "'"), ('â€œ', '"'), ('â€', '"'), ('â€"', '—'),
                ]
                
                for bad_char, good_char in encoding_fixes:
                    description = description.replace(bad_char, good_char)
                
                # Create course name
                if title:
                    course_name = f"{course_code} {title}"
                else:
                    course_name = course_code
                
                if course_name and description:
                    courses.append({
                        'Course Number and Name': course_name,
                        'Course Description': description
                    })
                    print(f"    Added: {course_name}")
    
    except ET.XMLSyntaxError as e:
        print(f"  XML parsing error: {e}")
    except Exception as e:
        print(f"  Unexpected error parsing XML: {e}")
    
    return courses

def test_single_subject(subject_code):
    """
    Test function to debug a single subject
    """
    print(f"Testing subject: {subject_code}")
    
    # Get XML data
    xml_content = get_course_data_xml(subject_code)
    
    if xml_content:
        print("XML content sample (first 500 chars):")
        print(xml_content[:500])
        print("\n" + "="*50 + "\n")
        
        # Parse the XML
        courses = parse_course_xml(xml_content)
        print(f"Found {len(courses)} courses for {subject_code}")
        
        if courses:
            print("\nSample courses:")
            for i, course in enumerate(courses[:3]):  # Show first 3
                print(f"{i+1}. {course['Course Number and Name']}")
                print(f"   Description: {course['Course Description'][:100]}...")
                print()
        
        return courses
    else:
        print("No XML content received")
        return []

def scrape_all_courses():
    """
    Main function to scrape all courses using the ribbit API
    """
    print("Starting SCAD course scraper using ribbit API...")
    
    # Get all course prefixes
    prefixes = get_course_prefixes()
    
    if not prefixes:
        print("No course prefixes found. Exiting.")
        return None
    
    print(f"Will process {len(prefixes)} subjects: {prefixes[:10]}...")
    
    all_courses = []
    
    # Process each prefix
    for i, prefix in enumerate(prefixes, 1):
        print(f"\nProcessing {prefix} ({i}/{len(prefixes)})")
        
        # Get XML data for this subject
        xml_content = get_course_data_xml(prefix)
        
        if xml_content:
            # Parse the XML and extract courses
            courses = parse_course_xml(xml_content)
            all_courses.extend(courses)
            print(f"  Total courses found for {prefix}: {len(courses)}")
        else:
            print(f"  No data received for {prefix}")
        
        # Be respectful - add delay between requests
        time.sleep(1)
    
    # Create DataFrame and save to CSV
    if all_courses:
        df = pd.DataFrame(all_courses)
        
        # Remove duplicates based on course name
        df = df.drop_duplicates(subset=['Course Number and Name'])
        
        # Save to CSV with UTF-8-BOM encoding (best for Excel compatibility)
        filename = 'scad_courses.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n🎉 Scraping complete!")
        print(f"Total courses found: {len(all_courses)}")
        print(f"Unique courses after deduplication: {len(df)}")
        print(f"Data saved to: {filename}")
        
        # Display summary
        print(f"\nSample of courses found:")
        for i, row in df.head(5).iterrows():
            print(f"{i+1}. {row['Course Number and Name']}")
        
        return df
    else:
        print("No courses found.")
        return None

# Quick test function
def quick_test():
    """
    Quick test to make sure everything works
    """
    print("Running quick test with ACCE...")
    test_courses = test_single_subject('ACCE')
    
    if test_courses:
        print(f"\n✅ Test successful! Found {len(test_courses)} ACCE courses")
        print("Ready to run full scraper.")
        return True
    else:
        print("\n❌ Test failed")
        return False

# Run functions
if __name__ == "__main__":
    # Run quick test first
    if quick_test():
        print("\n" + "="*60)
        user_input = input("Press Enter to run full scraper or 'n' to exit: ")
        if user_input.lower() != 'n':
            scrape_all_courses()
    else:
        print("Fix issues before running full scraper.")
