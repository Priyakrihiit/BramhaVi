# CMS Serializers Documentation

This document describes the 18 model serializers implemented under `backend/apps/cms/serializers.py` for the Enterprise CMS package of BrahmaVidya Galaxy.

---

## 1. Overview of Key Serializers

The following serializers extend `rest_framework.serializers.ModelSerializer` to support automated layouts, editorial status pipelines, role access lists, and integrations.

| Serializer | Associated Model | Key Fields & Validations | Nesting & Detail Payloads |
| :--- | :--- | :--- | :--- |
| **CategorySerializer** | `Category` | Name length, slug validation. | Recursively nests child categories as `children`. |
| **TagSerializer** | `Tag` | Slug validation. | Flat tag details. |
| **AuthorSerializer** | `Author` | Exposes associated user account email. | Used inside article author profiles. |
| **MediaFileSerializer** | `MediaFile` | Validates file size limits (<= 50MB). | Returns computed read-only physical URL of the uploaded asset. |
| **BlockTemplateSerializer** | `BlockTemplate` | Schema structures for page builder layouts. | Reads associated creator details. |
| **ContentBlockSerializer** | `ContentBlock` | Grid order, visibility rules. | Recursively nests layout grids as `children`. |
| **ArticleSerializer** | `Article` | Custom constraints on publication states and titles. | Nests categories (`categories_details`), tags (`tags_details`), and author metrics. |
| **FAQSerializer** | `FAQ` | Handles categorizations and page placement order. | Flat view formatting. |
| **ReactionSerializer** | `Reaction` | Restricts reactions from targeting both article and blog concurrently. | Associated reactor emails. |

---

## 2. Validation Constraints

Several validation routines are active across serializers:

1. **`validate_slug(value)`**: Restricts slugs to lowercase letters, numbers, and hyphens (`^[a-z0-9-]+$`).
2. **`validate_title(value)`**: Requires editorial headers to contain at least 3 characters.
3. **`validate_status(value)`**: Restricts states to defined choice limits (`draft`, `review`, `approved`, `published`, `archived`, `rejected`, `scheduled`).
4. **`validate_publish_date(value)`**: Ensures publication dates are not older than one year in the past.
5. **`validate_category(value)`**: Requires that at least one category is linked to the article payload.
6. **`validate_media(value)`**: Prevents non-image file uploads from being set as the hero or featured image.
7. **`validate(attrs)`**: Assertions on status transitions (e.g. enforcing status is set to `published` when the published toggle is checked).
