#Анализируется страница на все метрики

from bs4 import BeautifulSoup


def analyze_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"].strip() if description_tag and description_tag.get("content") else ""

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")

    images = soup.find_all("img")
    images_without_alt = [img for img in images if not img.get("alt")]

    text_content = soup.get_text(separator=" ")
    word_count = len(text_content.split())

    return {
        "title": title,
        "title_length": len(title),
        "meta_description_length": len(description),
        "h1_count": len(h1_tags),
        "h2_count": len(h2_tags),
        "total_images": len(images),
        "images_without_alt": len(images_without_alt),
        "word_count": word_count
    }