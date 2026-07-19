import re

class AISEOService:
    """
    Modular AI services to generate meta titles, descriptions, keyword suggestions,
    readability scores, and structured Schema.org markup.
    """
    @staticmethod
    def generate_meta_title(page_type, title, description=""):
        clean_title = title.strip()
        meta = f"{clean_title} | BrahmaVidya {page_type.title()}"
        return meta[:60]

    @staticmethod
    def generate_meta_description(page_type, title, description=""):
        desc = description or f"Discover the ultimate guide on {title}. Explore advanced learning, corporate services, and tutorials inside BrahmaVidya Galaxy."
        return desc[:160]

    @staticmethod
    def suggest_keywords(page_type, title, description=""):
        words = re.findall(r'\b\w{4,}\b', (title + " " + (description or "")).lower())
        keywords = list(set(words))[:6]
        default_keywords = ["brahmavidya", "learning", "education", page_type.lower()]
        return ", ".join(list(set(default_keywords + keywords)))

    @staticmethod
    def calculate_seo_score(meta_title, meta_description, keywords, schema_json):
        score = 60
        if meta_title and len(meta_title) >= 10:
            score += 10
        if meta_description and len(meta_description) >= 50:
            score += 15
        if keywords and len(keywords) > 5:
            score += 10
        if schema_json and isinstance(schema_json, dict) and len(schema_json.keys()) > 0:
            score += 5
        return min(score, 100)

    @staticmethod
    def generate_slug(title):
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug

    @staticmethod
    def suggest_internal_links(page_type, content=""):
        suggestions = [
            {"anchor": "BrahmaVidya Home", "url": "/"},
            {"anchor": "Explore Courses", "url": "/courses"},
            {"anchor": "AI Learning Assistant", "url": "/ai/tutor"},
        ]
        return suggestions

    @staticmethod
    def generate_schema_org(schema_type, name, description="", url="", extra_data=None):
        if not extra_data:
            extra_data = {}
            
        base_schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": name,
            "description": description or f"Structured representation of {name} on BrahmaVidya.",
            "url": url or f"https://brahmavidya.edu/{schema_type.lower()}/{name.lower().replace(' ', '-')}"
        }
        
        # Merge specific properties based on schema type
        if schema_type == "Course":
            base_schema.update({
                "provider": {
                    "@type": "Organization",
                    "name": "BrahmaVidya Galaxy",
                    "sameAs": "https://brahmavidya.edu"
                }
            })
        elif schema_type == "Article":
            base_schema.update({
                "headline": name,
                "author": {
                    "@type": "Person",
                    "name": extra_data.get("author_name", "BrahmaVidya Author")
                }
            })
        elif schema_type == "Book":
            base_schema.update({
                "isbn": extra_data.get("isbn", "000-0-00-000000-0"),
                "bookFormat": "https://schema.org/EBook"
            })
        elif schema_type == "Product":
            base_schema.update({
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "INR",
                    "price": str(extra_data.get("price", "0.00")),
                    "availability": "https://schema.org/InStock"
                }
            })
        elif schema_type == "FAQPage":
            base_schema.update({
                "@type": "FAQPage",
                "mainEntity": extra_data.get("questions", [
                    {
                        "@type": "Question",
                        "name": "What is BrahmaVidya Galaxy?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "An enterprise learning, publishing, and career development ecosystem."
                        }
                    }
                ])
            })
            # Remove "name" and "description" since FAQPage doesn't use standard ones
            base_schema.pop("name", None)
            base_schema.pop("description", None)
            
        return base_schema
