from apps.seo.models import SEOPage

class SEORepository:
    """
    Data repository layer managing query selections and updates for SEO pages and auditing metrics.
    """
    @staticmethod
    def get_by_type_and_id(page_type, page_id):
        return SEOPage.objects.filter(page_type=page_type.upper(), page_id=page_id).first()

    @staticmethod
    def get_or_create_page(page_type, page_id, defaults):
        return SEOPage.objects.get_or_create(
            page_type=page_type.upper(),
            page_id=page_id,
            defaults=defaults
        )

    @staticmethod
    def update_page_seo(page_type, page_id, updates):
        return SEOPage.objects.filter(page_type=page_type.upper(), page_id=page_id).update(**updates)
