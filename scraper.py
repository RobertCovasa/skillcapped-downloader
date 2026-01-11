from playwright.async_api import Page

async def scrape_details(page: Page, url: str):
    """Uses Playwright page to extract Course Name and Video Title."""
    print(f"[*] Scraping details for: {url}")
    try:
        # Fast load strategy: 'domcontentloaded' ignores heavy assets (video/images)
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for the Course Title element (Proof that JS loaded)
        try:
            await page.wait_for_selector(".css-1rwlwny", state="visible", timeout=10000)
        except:
            print(f"    [!] Timeout waiting for page content. Skipping auto-detect.")
            return None, None

        # 1. Course Name
        course_el = await page.query_selector(".css-1rwlwny")
        raw_course = await course_el.inner_text() if course_el else "Unknown Course"
        course_name = " ".join(raw_course.split()).title() # Clean & Title Case

        # 2. Video Title (Split across multiple divs)
        parts = await page.query_selector_all(".css-1juj8ih")
        title_words = []
        for part in parts:
            text = await part.inner_text()
            if text.strip():
                title_words.append(text.strip())
        
        video_title = " ".join(title_words).title() if title_words else "Unknown Video"

        print(f"    [+] Detected: {course_name} | {video_title}")
        return course_name, video_title

    except Exception as e:
        print(f"    [!] Scraper Error: {e}")
        return None, None