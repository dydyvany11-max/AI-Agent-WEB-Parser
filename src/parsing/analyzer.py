# analyzer.py
from bs4 import BeautifulSoup
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

    def get_images(self) -> List[Dict[str, str]]:
        images = []
        for img in self.soup.find_all("img"):
            images.append({
                "src": img.get("src", ""),
                "alt": img.get("alt", "")
            })
        return images

    def get_text_word_count(self) -> int:
        text_content = self.soup.get_text(separator=" ")
        return len(text_content.split())

    def analyze(self) -> Dict[str, Any]:
        images = self.get_images()
        images_without_alt = [img for img in images if not img["alt"]]

        return {
            "title": self.get_title(),
            "title_length": len(self.get_title()),
            "meta_description_length": len(self.get_meta_description()),
            "h1_count": len(self.get_headings(1)),
            "h2_count": len(self.get_headings(2)),
            "total_images": len(images),
            "images_without_alt": len(images_without_alt),
            "word_count": self.get_text_word_count()
        }
