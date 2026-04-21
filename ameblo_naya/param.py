import datetime

# Ameblo entry-list page to crawl.
# Example: "https://ameblo.jp/marysteatime/entrylist.html"
URL = "https://ameblo.jp/takeru-naya-we/entrylist.htmll"

# Base name for the exported link list file.
# Runtime output file name is generated as:
#   [base_name_without_ext]_[yyyyMMddHHmmss].txt
# Example:
#   blog_link_txt_name = "blog_link_190113.txt"
#   output file         = "blog_link_190113_20260421172400.txt"
blog_link_txt_name = 'blog_link_190113.txt'

# Crawl cutoff date.
# Only entries with publish date > latest_date are kept.
# Entries on or before this date are skipped.
# Example:
#   latest_date = datetime.date(2018, 1, 15)
#   kept    -> 2018-01-16, 2021-04-16
#   skipped -> 2018-01-15, 2017-12-31
latest_date = datetime.date(2025, 5, 1)

# Site prefix for normalizing relative links. Do not modify.
site_prefix = 'https://ameblo.jp'