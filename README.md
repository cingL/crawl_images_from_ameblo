# crawl_images_from_ameblo

This project crawls Ameblo entry links first, then downloads entry images.

## Python version
- Tested with: `Python 3.8.5`
- Recommended: `Python 3.8+`

## ameblo_naya (active)

### Files
- `param.py`: Runtime config.
- `crawl_url.py`: Crawl entry links from entry list pages.
- `crawl_image.py`: Download images from crawled entry links.
- `ameblo_naya/run.bat`: One-click launcher.
- `ameblo_naya/run.py`: Cross-platform Python launcher.

### Config (`ameblo_naya/param.py`)
- `URL`: Ameblo entry-list page URL.
  - Example: `https://ameblo.jp/marysteatime/entrylist.html`
- `blog_link_txt_name`: Base file name for link export.
  - Runtime output format: `[base_name]_[yyyyMMddHHmmss].txt`
  - Example: `1.txt` -> `1_20260421172400.txt`
- `latest_date`: Crawl cutoff date.
  - Keep entries with `publish_date > latest_date`
  - Skip entries on or before this date
- `site_prefix`: Site prefix for normalizing relative links. Do not modify.

### Runtime outputs
- Link file: `ameblo_naya/[blog_link_txt_name_without_ext]_[timestamp].txt`
- Result directory: `ameblo_naya/[timestamp]_result`
- Image file: `[entry_date]_[entry_title]-[index].[ext]`

### How to run
- Windows: double-click `ameblo_naya/run.bat`
- Cross-platform: `python ameblo_naya/run.py`
- Or run manually:
  1) `python ameblo_naya/crawl_url.py`
  2) `python ameblo_naya/crawl_image.py`

## ameblo_zaiki (legacy)

This folder keeps the older crawler scripts.
Update `ameblo_zaiki/param.py` before running.
