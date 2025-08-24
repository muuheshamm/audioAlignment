from rich import print
from playwright.sync_api import sync_playwright
from time import sleep
import json

custom_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
}
video_tresor = []


def run_spider(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 1080})
        page.set_extra_http_headers(custom_headers)
        page.context.set_default_timeout(60000)

        page.goto(url)
        page.wait_for_load_state('networkidle')
        sleep(5)

        title = page.title()
        if title == "Before you continue to YouTube":
            button = page.locator('button[aria-label="Reject all"]').first
            button.click()

        page.wait_for_load_state('networkidle')
        page.focus("body")
        more_to_load = True

        while more_to_load:
            videos_before = page.locator('#content.style-scope.ytd-rich-item-renderer').count()
            page.keyboard.press('End')
            page.keyboard.press('End')
            page.keyboard.press('End')
            sleep(1.5)
            videos_after = page.locator('#content.style-scope.ytd-rich-item-renderer').count()

            print("videos before", videos_before)
            print("videos after", videos_after)
            if videos_before == videos_after:
                more_to_load = False
                print('we reached the end')

        videos = page.locator('#content.style-scope.ytd-rich-item-renderer')
        for idx in range(videos.count()):
            video = videos.nth(idx)

            thumbnail_image = video.locator('#thumbnail img').first
            thumbnail = thumbnail_image.get_attribute('src')
            print(f"thumbnail {thumbnail}")

            video_id = None
            if thumbnail:
                try:
                    start = thumbnail.index("vi/") + 3
                    end = thumbnail.index("/", start)
                    video_id = thumbnail[start:end]
                except ValueError:
                    video_id = None

            # Generate YouTube video URL
            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None

            title = video.locator('h3 #video-title').text_content()
            print(f"title {title}")

            views_text = video.locator('#metadata #metadata-line span').first.text_content()
            views = views_text.replace('views', '').strip().lower()
            if 'k' in views:
                views = float(views.replace('k', '').strip()) * 1000
            elif 'm' in views:
                views = float(views.replace('m', '').strip()) * 1000000
            else:
                try:
                    views = float(views.strip())
                except ValueError:
                    views = 0  # fallback if can't parse
            print(f"views {views}")

            upload = video.locator('#metadata #metadata-line span').last.text_content()
            print(f"upload {upload}")

            duration_selector = '#thumbnail #overlays ytd-thumbnail-overlay-time-status-renderer #time-status span#text'
            duration = video.locator(duration_selector).first.text_content()
            duration = duration.replace('\n', '').strip()
            print(f"duration {duration}")

            video_obj = {
                'thumbnail': thumbnail,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'views': views,
                'upload': upload,
                'duration': duration
            }
            print(video_obj)
            video_tresor.append(video_obj)

        # Save data to JSON file
        with open("videos.json", "w", encoding="utf-8") as json_file:
            json.dump(video_tresor, json_file, ensure_ascii=False, indent=4)

        print(f"Total videos scraped: {len(video_tresor)}")
        print(f"Data saved to videos.json")

        sleep(10)
        browser.close()


run_spider(url='https://www.youtube.com/@communityofbabel/videos')