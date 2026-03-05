# analyzer.py
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Any, Dict, List

class HtmlAnalyzer:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def get_title(self) -> str:
        return self.soup.title.string.strip() if self.soup.title and self.soup.title.string else ""

    def get_meta_description(self) -> str:
        tag = self.soup.find("meta", attrs={"name": "description"})
        return tag["content"].strip() if tag and tag.get("content") else ""

    def get_headings(self, level: int = 1) -> List[str]:
        if level not in range(1, 7):
            return []
        return [h.text.strip() for h in self.soup.find_all(f"h{level}")]

    def get_canonical_url(self) -> str:
        tag = self.soup.find("link", attrs={"rel": "canonical"})
        return tag.get("href", "").strip() if tag else ""

    def get_meta_robots(self) -> str:
        tag = self.soup.find("meta", attrs={"name": "robots"})
        return tag.get("content", "").strip() if tag else ""

    def get_html_lang(self) -> str:
        html_tag = self.soup.find("html")
        return html_tag.get("lang", "").strip() if html_tag else ""

    def get_images(self) -> List[Dict[str, str]]:
        images = []
        for img in self.soup.find_all("img"):
            images.append({
                "src": img.get("src", ""),
                "alt": img.get("alt", "")
            })
        return images

    def get_links(self) -> List[Dict[str, Any]]:
        links = []
        for a in self.soup.find_all("a"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            parsed = urlparse(href)
            is_external = bool(parsed.scheme and parsed.netloc)
            links.append({
                "href": href,
                "is_external": is_external
            })
        return links

    def get_open_graph(self) -> Dict[str, str]:
        og_title = self.soup.find("meta", attrs={"property": "og:title"})
        og_description = self.soup.find("meta", attrs={"property": "og:description"})
        return {
            "og_title": og_title.get("content", "").strip() if og_title else "",
            "og_description": og_description.get("content", "").strip() if og_description else "",
        }

    def get_structured_data_count(self) -> int:
        return len(self.soup.find_all("script", attrs={"type": "application/ld+json"}))

    def get_text_word_count(self) -> int:
        text_content = self.soup.get_text(separator=" ")
        return len(text_content.split())

    def analyze(self) -> Dict[str, Any]:
        title = self.get_title()
        meta_description = self.get_meta_description()
        canonical_url = self.get_canonical_url()
        meta_robots = self.get_meta_robots()
        html_lang = self.get_html_lang()
        images = self.get_images()
        links = self.get_links()
        og = self.get_open_graph()
        images_without_alt = [img for img in images if not img["alt"]]
        internal_links = [link for link in links if not link["is_external"]]
        external_links = [link for link in links if link["is_external"]]

        return {
            "title": title,
            "title_length": len(title),
            "title_too_short": len(title) < 30,
            "title_too_long": len(title) > 60,
            "meta_description": meta_description,
            "meta_description_length": len(meta_description),
            "meta_description_missing": len(meta_description) == 0,
            "h1_count": len(self.get_headings(1)),
            "h2_count": len(self.get_headings(2)),
            "h3_count": len(self.get_headings(3)),
            "canonical_url": canonical_url,
            "has_canonical": len(canonical_url) > 0,
            "meta_robots": meta_robots,
            "lang": html_lang,
            "total_links": len(links),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "total_images": len(images),
            "images_without_alt": len(images_without_alt),
            "word_count": self.get_text_word_count(),
            "og_title_present": len(og["og_title"]) > 0,
            "og_description_present": len(og["og_description"]) > 0,
            "structured_data_count": self.get_structured_data_count(),
        }
