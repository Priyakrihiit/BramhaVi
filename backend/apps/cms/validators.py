"""
CMS Production Validators - BrahmaVidya Galaxy
Sprint 15 — Enterprise CMS Extension

Purpose:
    Centralised, reusable validation functions and Django validator callables
    for every data surface the CMS accepts: slugs, URLs, HTML, Markdown,
    file uploads, SEO metadata, workflow transitions, and publish schedules.

Design rules:
    - Every validator raises django.core.exceptions.ValidationError with a
      human-readable, field-specific message on failure.
    - Pure functions — no DB writes, no side effects.
    - DB-level uniqueness validators accept an optional `exclude_id` argument
      for safe use on PATCH (partial update) operations.
    - File validators accept Django UploadedFile objects directly.
    - All validators are importable individually for use in serializer fields
      or model clean() methods.

Usage examples:
    # In a DRF serializer field:
    slug = serializers.SlugField(validators=[validate_cms_slug])

    # In a serializer's validate_<field>:
    def validate_slug(self, value):
        validate_cms_slug(value)
        validate_no_reserved_url(value)
        return value

    # For file uploads:
    def validate_image(self, value):
        validate_upload_image(value)
        return value
"""

from __future__ import annotations

import re
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger("cms.validators")


# ─────────────────────────────────────────────────────────────────────────────
# EXISTING VALIDATOR — PRESERVED EXACTLY
# ─────────────────────────────────────────────────────────────────────────────

APPROVED_BLOCK_TYPES = {
    "HERO", "TEXT_COLUMN", "VIDEO_PLAYER", "GRID_NAVIGATOR", "ENROLLMENT_ACCORDION"
}


def validate_page_layout_schema(layout_blocks: List[Dict[str, Any]]) -> None:
    """
    Validates that every node in the block array matches the required format schemas:
    - Must possess a unique 'id' string.
    - Must specify an approved 'type'.
    - Must possess a dictionary containing block 'properties'.
    """
    if not isinstance(layout_blocks, list):
        raise ValidationError("Layout payload must be a list array of blocks.")

    for index, block in enumerate(layout_blocks):
        if not isinstance(block, dict):
            raise ValidationError(f"Block at position {index} is not a valid JSON object.")

        if "id" not in block or not isinstance(block["id"], str):
            raise ValidationError(
                f"Block at position {index} is missing a unique string 'id' attribute."
            )

        block_type = block.get("type")
        if block_type not in APPROVED_BLOCK_TYPES:
            raise ValidationError(
                f"Block at position {index} has unsupported type: '{block_type}'. "
                f"Approved types: {APPROVED_BLOCK_TYPES}"
            )

        if "properties" not in block or not isinstance(block["properties"], dict):
            raise ValidationError(
                f"Block at position {index} must possess a valid 'properties' dictionary object."
            )


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Slug — allowed chars: a-z, 0-9, hyphen. Must start and end with alphanumeric.
_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$')
_SLUG_SINGLE_CHAR_RE = re.compile(r'^[a-z0-9]$')
_SLUG_CONSECUTIVE_HYPHENS_RE = re.compile(r'--')

# CMS reserved URL paths — these paths are used by the platform itself
# and must never be used as content slugs.
CMS_RESERVED_SLUGS: set = {
    "admin", "api", "auth", "login", "logout", "register", "signup",
    "dashboard", "cms", "settings", "profile", "account", "accounts",
    "static", "media", "assets", "favicon", "robots", "sitemap",
    "health", "ping", "status", "metrics", "debug", "test",
    "null", "undefined", "true", "false",
    "about", "contact", "help", "support", "pricing", "terms",
    "privacy", "legal", "cookies", "disclaimer",
    "404", "500", "error", "not-found",
}

# Allowed MIME types — by category
ALLOWED_IMAGE_MIME: set = {
    "image/jpeg", "image/png", "image/gif",
    "image/webp", "image/svg+xml",
}
ALLOWED_VIDEO_MIME: set = {
    "video/mp4", "video/webm", "video/ogg", "video/quicktime",
}
ALLOWED_AUDIO_MIME: set = {
    "audio/mpeg", "audio/ogg", "audio/wav", "audio/aac", "audio/flac",
}
ALLOWED_PDF_MIME: set = {"application/pdf"}
ALLOWED_DOCUMENT_MIME: set = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
ALL_ALLOWED_MIME: set = (
    ALLOWED_IMAGE_MIME | ALLOWED_VIDEO_MIME |
    ALLOWED_AUDIO_MIME | ALLOWED_DOCUMENT_MIME
)

# Upload size limits (bytes)
MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024      # 10 MB
MAX_VIDEO_SIZE_BYTES: int = 500 * 1024 * 1024     # 500 MB
MAX_AUDIO_SIZE_BYTES: int = 50 * 1024 * 1024      # 50 MB
MAX_PDF_SIZE_BYTES: int = 25 * 1024 * 1024        # 25 MB
MAX_DOCUMENT_SIZE_BYTES: int = 25 * 1024 * 1024   # 25 MB
MAX_GENERIC_SIZE_BYTES: int = 50 * 1024 * 1024    # 50 MB fallback

# Allowed file extensions (defence-in-depth alongside MIME checks)
ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".webm", ".ogg", ".mov"}
ALLOWED_AUDIO_EXTENSIONS: set = {".mp3", ".ogg", ".wav", ".aac", ".flac"}
ALLOWED_PDF_EXTENSIONS: set = {".pdf"}
ALLOWED_DOCUMENT_EXTENSIONS: set = {
    ".pdf", ".doc", ".docx", ".txt", ".md", ".csv", ".xls", ".xlsx"
}

# HTML tags we strip/reject in user-submitted body content
_DANGEROUS_HTML_TAGS: set = {
    "script", "iframe", "object", "embed", "applet",
    "form", "input", "button", "select", "textarea",
    "link", "meta", "base", "style",
}
_HTML_TAG_RE = re.compile(r'<\s*([a-zA-Z][a-zA-Z0-9]*)', re.IGNORECASE)

# Workflow valid transitions (mirrors WorkflowService.VALID_TRANSITIONS)
WORKFLOW_VALID_TRANSITIONS: Dict[str, List[str]] = {
    "draft":     ["submitted", "archived"],
    "submitted": ["review", "draft", "rejected"],
    "review":    ["approved", "rejected", "draft"],
    "approved":  ["published", "scheduled", "rejected"],
    "rejected":  ["draft"],
    "published": ["archived", "draft"],
    "archived":  ["draft"],
    "scheduled": ["published", "draft", "cancelled"],
}

# SEO limits
SEO_META_TITLE_MAX: int = 70
SEO_META_TITLE_MIN: int = 10
SEO_META_DESC_MAX: int = 160
SEO_META_DESC_MIN: int = 50

# File name — disallow path traversal and special chars
_SAFE_FILENAME_RE = re.compile(r'^[\w\-. ]+$')
_DANGEROUS_FILENAME_PATTERNS = ["..", "/", "\\", "\x00"]


# ─────────────────────────────────────────────────────────────────────────────
# SLUG VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_cms_slug(value: str) -> None:
    """
    Validate a CMS content slug.

    Rules:
        - Lowercase alphanumeric characters and hyphens only.
        - Must start and end with an alphanumeric character.
        - No consecutive hyphens.
        - Minimum 2 characters, maximum 128 characters.

    Args:
        value: The slug string to validate.

    Raises:
        ValidationError: On any rule violation.
    """
    if not value:
        raise ValidationError("Slug must not be empty.")

    value = value.strip()

    if len(value) < 2:
        raise ValidationError("Slug must be at least 2 characters long.")

    if len(value) > 128:
        raise ValidationError(
            f"Slug must not exceed 128 characters (got {len(value)})."
        )

    if value != value.lower():
        raise ValidationError("Slug must be lowercase only. Use hyphens instead of spaces.")

    # Single-char slugs use a simpler pattern
    if len(value) == 1:
        if not _SLUG_SINGLE_CHAR_RE.match(value):
            raise ValidationError("Slug must contain only lowercase letters or digits.")
        return

    if not _SLUG_RE.match(value):
        raise ValidationError(
            "Slug may only contain lowercase letters (a-z), digits (0-9), and hyphens. "
            "It must start and end with a letter or digit."
        )

    if _SLUG_CONSECUTIVE_HYPHENS_RE.search(value):
        raise ValidationError("Slug must not contain consecutive hyphens (--).")


def validate_no_reserved_url(value: str) -> None:
    """
    Reject slugs that collide with reserved platform URL paths.

    Args:
        value: The slug to check.

    Raises:
        ValidationError: If the slug matches a reserved path.
    """
    if value.lower().strip() in CMS_RESERVED_SLUGS:
        raise ValidationError(
            f"'{value}' is a reserved URL path and cannot be used as a content slug. "
            f"Choose a different slug."
        )


def validate_unique_article_slug(value: str, exclude_id=None) -> None:
    """
    Validate that an Article slug is unique (across non-deleted articles).

    Safe for use in PATCH operations via the exclude_id argument.

    Args:
        value: The slug to check.
        exclude_id: UUID of the article being updated (excluded from uniqueness check).

    Raises:
        ValidationError: If a different article already uses this slug.
    """
    from apps.cms.models import Article
    qs = Article.objects.filter(slug=value, deleted_at__isnull=True)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise ValidationError(
            f"An article with slug '{value}' already exists. "
            f"Slugs must be unique across all non-deleted articles."
        )


def validate_unique_page_slug(value: str, exclude_id=None) -> None:
    """
    Validate that a Page slug is unique (across non-deleted pages).

    Args:
        value: The slug to check.
        exclude_id: UUID of the page being updated.

    Raises:
        ValidationError: If a different page already uses this slug.
    """
    from apps.cms.models import Page
    qs = Page.objects.filter(slug=value, deleted_at__isnull=True)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise ValidationError(
            f"A page with slug '{value}' already exists. Page slugs must be unique."
        )


def validate_unique_blog_slug(value: str, exclude_id=None) -> None:
    """
    Validate that a Blog slug is unique (across non-deleted blogs).

    Args:
        value: The slug to check.
        exclude_id: UUID of the blog being updated.

    Raises:
        ValidationError: If a different blog already uses this slug.
    """
    from apps.cms.models import Blog
    qs = Blog.objects.filter(slug=value, deleted_at__isnull=True)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise ValidationError(
            f"A blog post with slug '{value}' already exists. Blog slugs must be unique."
        )


def validate_unique_category_slug(value: str, exclude_id=None) -> None:
    """
    Validate that a Category slug is unique.

    Args:
        value: The slug to check.
        exclude_id: UUID of the category being updated.

    Raises:
        ValidationError: If a different category already uses this slug.
    """
    from apps.cms.models import Category
    qs = Category.objects.filter(slug=value, deleted_at__isnull=True)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise ValidationError(
            f"A category with slug '{value}' already exists."
        )


def validate_unique_tag_slug(value: str, exclude_id=None) -> None:
    """
    Validate that a Tag slug is unique.

    Args:
        value: The slug to check.
        exclude_id: UUID of the tag being updated.

    Raises:
        ValidationError: If a different tag already uses this slug.
    """
    from apps.cms.models import Tag
    qs = Tag.objects.filter(slug=value)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    if qs.exists():
        raise ValidationError(
            f"A tag with slug '{value}' already exists."
        )


# ─────────────────────────────────────────────────────────────────────────────
# HTML & MARKDOWN VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_no_dangerous_html(value: str) -> None:
    """
    Reject content containing dangerous HTML tags.

    Scans for <script>, <iframe>, <form>, <object>, <embed>, <applet>,
    <input>, <button>, <select>, <textarea>, <link>, <meta>, <base>, <style>.

    This is a defence-in-depth check alongside server-side HTML sanitization
    (bleach/nh3). It is intentionally conservative — it rejects the submission
    immediately so editors receive instant feedback.

    Args:
        value: HTML or Markdown string to validate.

    Raises:
        ValidationError: If a dangerous tag is found.
    """
    if not value:
        return

    tags_found = _HTML_TAG_RE.findall(value)
    dangerous = [t for t in tags_found if t.lower() in _DANGEROUS_HTML_TAGS]

    if dangerous:
        unique_dangerous = sorted(set(t.lower() for t in dangerous))
        raise ValidationError(
            f"Content contains forbidden HTML tags: {unique_dangerous}. "
            f"Tags such as <script>, <iframe>, <form>, and <style> are not allowed."
        )


def validate_html_sanitization(value: str, max_length: int = 500_000) -> str:
    """
    Sanitize HTML content using the `nh3` library (Rust-based html sanitizer).

    Falls back gracefully if nh3 is not installed — logs a warning and
    returns the original value (the dangerous-tag regex check above still runs).

    Allowed tags are a safe subset: headings, paragraphs, lists, code blocks,
    blockquotes, links, images, tables, and standard inline formatting.

    Args:
        value: Raw HTML string.
        max_length: Reject values exceeding this byte length.

    Returns:
        Sanitized HTML string.

    Raises:
        ValidationError: If content exceeds max_length.
    """
    if not value:
        return value

    if len(value) > max_length:
        raise ValidationError(
            f"Content exceeds maximum allowed length of {max_length:,} characters."
        )

    try:
        import nh3
        allowed_tags = {
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "br", "hr",
            "strong", "b", "em", "i", "u", "s", "del", "ins", "mark", "small",
            "ul", "ol", "li", "dl", "dt", "dd",
            "pre", "code", "kbd", "samp",
            "blockquote", "cite", "q",
            "a", "img",
            "table", "thead", "tbody", "tfoot", "tr", "th", "td",
            "div", "span", "section", "article", "aside", "header", "footer",
            "figure", "figcaption",
            "sup", "sub",
        }
        allowed_attributes = {
            "a": {"href", "title", "target", "rel"},
            "img": {"src", "alt", "title", "width", "height", "loading"},
            "th": {"scope", "colspan", "rowspan"},
            "td": {"colspan", "rowspan"},
            "*": {"class", "id"},
        }
        return nh3.clean(value, tags=allowed_tags, attributes=allowed_attributes)
    except ImportError:
        logger.warning(
            "nh3 not installed — HTML sanitization skipped. "
            "Install with: pip install nh3"
        )
        return value


def validate_markdown_content(value: str, max_length: int = 500_000) -> None:
    """
    Validate a Markdown content field.

    Checks:
        - Not empty / whitespace-only.
        - Does not exceed max_length.
        - Does not contain raw dangerous HTML tags (Markdown allows inline HTML).

    Args:
        value: Markdown string.
        max_length: Maximum allowed length in characters.

    Raises:
        ValidationError: On any rule violation.
    """
    if not value or not value.strip():
        raise ValidationError("Content must not be empty or whitespace only.")

    if len(value) > max_length:
        raise ValidationError(
            f"Content exceeds the maximum allowed length of {max_length:,} characters."
        )

    # Even in Markdown, inline HTML is parsed — reject dangerous tags
    validate_no_dangerous_html(value)


# ─────────────────────────────────────────────────────────────────────────────
# FILE NAME VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

def validate_safe_filename(filename: str) -> None:
    """
    Reject filenames that contain path traversal sequences or shell-dangerous characters.

    Rules:
        - No directory separators (/ or \\).
        - No null bytes.
        - No parent directory references (..).
        - Only: word characters, hyphens, dots, spaces.
        - Maximum 255 characters.

    Args:
        filename: The original filename string (not the upload path).

    Raises:
        ValidationError: If the filename is unsafe.
    """
    if not filename:
        raise ValidationError("File name must not be empty.")

    if len(filename) > 255:
        raise ValidationError(
            f"File name must not exceed 255 characters (got {len(filename)})."
        )

    for pattern in _DANGEROUS_FILENAME_PATTERNS:
        if pattern in filename:
            raise ValidationError(
                f"File name contains a forbidden character or sequence: '{pattern}'."
            )

    if not _SAFE_FILENAME_RE.match(filename):
        raise ValidationError(
            "File name contains invalid characters. Only letters, digits, "
            "hyphens (-), underscores (_), dots (.), and spaces are allowed."
        )


# ─────────────────────────────────────────────────────────────────────────────
# MIME TYPE VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_mime_type(mime_type: str, allowed: set, label: str = "file") -> None:
    """
    Validate that a MIME type is in an allowed set.

    Args:
        mime_type: The MIME type string (e.g. "image/jpeg").
        allowed: Set of allowed MIME type strings.
        label: Human-readable file category for the error message.

    Raises:
        ValidationError: If the MIME type is not allowed.
    """
    if not mime_type:
        raise ValidationError(f"Could not determine {label} MIME type.")

    if mime_type not in allowed:
        raise ValidationError(
            f"File type '{mime_type}' is not allowed for {label} uploads. "
            f"Allowed types: {sorted(allowed)}"
        )


def validate_any_allowed_mime(mime_type: str) -> None:
    """
    Validate that a MIME type is in the global allowed set for CMS uploads.

    Args:
        mime_type: MIME type string.

    Raises:
        ValidationError: If not in the global allowlist.
    """
    validate_mime_type(mime_type, ALL_ALLOWED_MIME, label="CMS")


# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD SIZE VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def _check_file_size(file_obj, max_bytes: int, label: str) -> None:
    """
    Internal helper — validates upload file size.

    Args:
        file_obj: Django InMemoryUploadedFile or TemporaryUploadedFile.
        max_bytes: Maximum allowed file size in bytes.
        label: Human-readable category name for error messages.

    Raises:
        ValidationError: If file exceeds size limit.
    """
    size = getattr(file_obj, "size", None)
    if size is None:
        try:
            size = file_obj.seek(0, 2)
            file_obj.seek(0)
        except Exception:
            logger.warning("Could not determine upload file size.")
            return

    max_mb = max_bytes / (1024 * 1024)
    if size > max_bytes:
        actual_mb = size / (1024 * 1024)
        raise ValidationError(
            f"{label} file size {actual_mb:.1f} MB exceeds the maximum "
            f"allowed size of {max_mb:.0f} MB."
        )


def validate_upload_image(file_obj) -> None:
    """
    Validate an uploaded image file.

    Checks:
        - MIME type is an allowed image type.
        - File extension matches allowed image extensions.
        - File size does not exceed 10 MB.

    Args:
        file_obj: Django UploadedFile instance.

    Raises:
        ValidationError: On any rule violation.
    """
    mime_type = getattr(file_obj, "content_type", "")
    validate_mime_type(mime_type, ALLOWED_IMAGE_MIME, label="image")

    ext = os.path.splitext(getattr(file_obj, "name", ""))[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Image extension '{ext}' is not allowed. "
            f"Allowed extensions: {sorted(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    validate_safe_filename(getattr(file_obj, "name", ""))
    _check_file_size(file_obj, MAX_IMAGE_SIZE_BYTES, "Image")


def validate_upload_video(file_obj) -> None:
    """
    Validate an uploaded video file.

    Checks:
        - MIME type is an allowed video type.
        - File extension matches allowed video extensions.
        - File size does not exceed 500 MB.

    Args:
        file_obj: Django UploadedFile instance.

    Raises:
        ValidationError: On any rule violation.
    """
    mime_type = getattr(file_obj, "content_type", "")
    validate_mime_type(mime_type, ALLOWED_VIDEO_MIME, label="video")

    ext = os.path.splitext(getattr(file_obj, "name", ""))[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f"Video extension '{ext}' is not allowed. "
            f"Allowed extensions: {sorted(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    validate_safe_filename(getattr(file_obj, "name", ""))
    _check_file_size(file_obj, MAX_VIDEO_SIZE_BYTES, "Video")


def validate_upload_pdf(file_obj) -> None:
    """
    Validate an uploaded PDF file.

    Checks:
        - MIME type is application/pdf.
        - File extension is .pdf.
        - File size does not exceed 25 MB.

    Args:
        file_obj: Django UploadedFile instance.

    Raises:
        ValidationError: On any rule violation.
    """
    mime_type = getattr(file_obj, "content_type", "")
    validate_mime_type(mime_type, ALLOWED_PDF_MIME, label="PDF")

    ext = os.path.splitext(getattr(file_obj, "name", ""))[1].lower()
    if ext not in ALLOWED_PDF_EXTENSIONS:
        raise ValidationError(
            f"Only .pdf files are accepted. Got: '{ext}'"
        )

    validate_safe_filename(getattr(file_obj, "name", ""))
    _check_file_size(file_obj, MAX_PDF_SIZE_BYTES, "PDF")


def validate_upload_document(file_obj) -> None:
    """
    Validate an uploaded document file (PDF, Word, Excel, text, CSV, Markdown).

    Checks:
        - MIME type is in ALLOWED_DOCUMENT_MIME.
        - File extension is in ALLOWED_DOCUMENT_EXTENSIONS.
        - File size does not exceed 25 MB.

    Args:
        file_obj: Django UploadedFile instance.

    Raises:
        ValidationError: On any rule violation.
    """
    mime_type = getattr(file_obj, "content_type", "")
    validate_mime_type(mime_type, ALLOWED_DOCUMENT_MIME, label="document")

    ext = os.path.splitext(getattr(file_obj, "name", ""))[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"Document extension '{ext}' is not allowed. "
            f"Allowed: {sorted(ALLOWED_DOCUMENT_EXTENSIONS)}"
        )

    validate_safe_filename(getattr(file_obj, "name", ""))
    _check_file_size(file_obj, MAX_DOCUMENT_SIZE_BYTES, "Document")


def validate_upload_any(file_obj) -> None:
    """
    Validate any CMS media upload — delegates to the correct type validator
    based on MIME type.

    Args:
        file_obj: Django UploadedFile instance.

    Raises:
        ValidationError: If type is unknown or validation fails.
    """
    mime_type = getattr(file_obj, "content_type", "")
    if mime_type in ALLOWED_IMAGE_MIME:
        validate_upload_image(file_obj)
    elif mime_type in ALLOWED_VIDEO_MIME:
        validate_upload_video(file_obj)
    elif mime_type in ALLOWED_AUDIO_MIME:
        validate_safe_filename(getattr(file_obj, "name", ""))
        _check_file_size(file_obj, MAX_AUDIO_SIZE_BYTES, "Audio")
    elif mime_type in ALLOWED_PDF_MIME:
        validate_upload_pdf(file_obj)
    elif mime_type in ALLOWED_DOCUMENT_MIME:
        validate_upload_document(file_obj)
    else:
        raise ValidationError(
            f"File type '{mime_type}' is not supported. "
            f"Supported categories: images, videos, audio, PDFs, documents."
        )


# ─────────────────────────────────────────────────────────────────────────────
# SEO METADATA VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_seo_meta_title(value: str) -> None:
    """
    Validate an SEO meta title.

    Rules:
        - Not empty.
        - Between 10 and 70 characters (Google truncates > 70).
        - No dangerous HTML tags.

    Args:
        value: Meta title string.

    Raises:
        ValidationError: On any rule violation.
    """
    if not value or not value.strip():
        raise ValidationError("SEO meta title must not be empty.")

    stripped = value.strip()

    if len(stripped) < SEO_META_TITLE_MIN:
        raise ValidationError(
            f"SEO meta title must be at least {SEO_META_TITLE_MIN} characters "
            f"(got {len(stripped)})."
        )

    if len(stripped) > SEO_META_TITLE_MAX:
        raise ValidationError(
            f"SEO meta title must not exceed {SEO_META_TITLE_MAX} characters "
            f"(got {len(stripped)}). Google truncates titles longer than 70 characters."
        )

    validate_no_dangerous_html(stripped)


def validate_seo_meta_description(value: str) -> None:
    """
    Validate an SEO meta description.

    Rules:
        - Not empty.
        - Between 50 and 160 characters (Google truncates > 160).
        - No dangerous HTML tags.

    Args:
        value: Meta description string.

    Raises:
        ValidationError: On any rule violation.
    """
    if not value or not value.strip():
        raise ValidationError("SEO meta description must not be empty.")

    stripped = value.strip()

    if len(stripped) < SEO_META_DESC_MIN:
        raise ValidationError(
            f"SEO meta description must be at least {SEO_META_DESC_MIN} characters "
            f"(got {len(stripped)}). Short descriptions are penalised by search engines."
        )

    if len(stripped) > SEO_META_DESC_MAX:
        raise ValidationError(
            f"SEO meta description must not exceed {SEO_META_DESC_MAX} characters "
            f"(got {len(stripped)}). Google truncates descriptions longer than 160 characters."
        )

    validate_no_dangerous_html(stripped)


def validate_canonical_url(value: str) -> None:
    """
    Validate a canonical URL — must be an absolute HTTPS URL or a relative path.

    Accepts:
        - Absolute HTTPS URLs: "https://brahmavidya.com/articles/my-article/"
        - Relative paths: "/articles/my-article/"

    Rejects:
        - HTTP (non-secure) absolute URLs.
        - JavaScript URLs (javascript:...).
        - Data URLs (data:...).

    Args:
        value: Canonical URL string.

    Raises:
        ValidationError: If the URL is invalid or insecure.
    """
    if not value:
        return  # Canonical URL is optional

    value = value.strip()

    if value.lower().startswith("javascript:"):
        raise ValidationError("Canonical URL must not be a JavaScript URL.")

    if value.lower().startswith("data:"):
        raise ValidationError("Canonical URL must not be a data: URL.")

    if value.startswith("http://"):
        raise ValidationError(
            "Canonical URL must use HTTPS, not HTTP. "
            "Example: https://brahmavidya.com/articles/my-article/"
        )

    # Must be either relative path or https absolute
    if not (value.startswith("/") or value.startswith("https://")):
        raise ValidationError(
            "Canonical URL must be a relative path (e.g. /articles/slug/) "
            "or an absolute HTTPS URL (e.g. https://example.com/articles/slug/)."
        )


def validate_og_image_url(value: str) -> None:
    """
    Validate an OpenGraph image URL.

    Must be an absolute HTTPS URL pointing to a supported image format.

    Args:
        value: OG image URL string.

    Raises:
        ValidationError: If invalid.
    """
    if not value:
        return  # OG image is optional

    value = value.strip()

    if not value.startswith("https://"):
        raise ValidationError(
            "OpenGraph image URL must be an absolute HTTPS URL. "
            "Example: https://cdn.brahmavidya.com/images/og-article.jpg"
        )

    ext = os.path.splitext(value.split("?")[0])[1].lower()
    if ext and ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        raise ValidationError(
            f"OpenGraph image should be a JPEG, PNG, GIF, or WebP file. "
            f"Got extension: '{ext}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_workflow_transition(from_status: str, to_status: str) -> None:
    """
    Validate that a workflow status transition is permitted.

    Uses the same transition map as WorkflowService to ensure
    serializers and services stay in sync.

    Args:
        from_status: Current workflow status.
        to_status: Requested new workflow status.

    Raises:
        ValidationError: If the transition is not allowed.
    """
    if from_status not in WORKFLOW_VALID_TRANSITIONS:
        raise ValidationError(
            f"Unknown workflow status: '{from_status}'. "
            f"Valid statuses: {sorted(WORKFLOW_VALID_TRANSITIONS.keys())}"
        )

    allowed_next = WORKFLOW_VALID_TRANSITIONS[from_status]
    if to_status not in allowed_next:
        raise ValidationError(
            f"Cannot transition from '{from_status}' to '{to_status}'. "
            f"Allowed transitions from '{from_status}': {allowed_next}"
        )


def validate_workflow_comment_required(to_status: str, comment: Optional[str]) -> None:
    """
    Require a reviewer comment when rejecting content.

    Editors must always provide a reason when rejecting so authors
    know what to fix.

    Args:
        to_status: The target workflow status.
        comment: The reviewer's comment string.

    Raises:
        ValidationError: If rejecting without a comment.
    """
    if to_status == "rejected" and not (comment and comment.strip()):
        raise ValidationError(
            "A comment explaining the reason for rejection is required."
        )


def validate_workflow_assignment(to_status: str, assigned_to_id: Optional[str]) -> None:
    """
    Require a reviewer assignment when moving content into review.

    Args:
        to_status: The target workflow status.
        assigned_to_id: UUID string of the assigned reviewer.

    Raises:
        ValidationError: If moving to review without assigning a reviewer.
    """
    if to_status in ("submitted", "review") and not assigned_to_id:
        raise ValidationError(
            f"A reviewer must be assigned when moving content to '{to_status}' status."
        )


# ─────────────────────────────────────────────────────────────────────────────
# PUBLISH DATE & SCHEDULE VALIDATORS
# ─────────────────────────────────────────────────────────────────────────────

def validate_publish_date_not_past(scheduled_at) -> None:
    """
    Validate that a scheduled publish datetime is in the future.

    Args:
        scheduled_at: datetime object (timezone-aware or naive).

    Raises:
        ValidationError: If the datetime is in the past.
    """
    if not scheduled_at:
        raise ValidationError("Scheduled publish time must not be empty.")

    now = timezone.now()

    # Make timezone-aware if naive
    if hasattr(scheduled_at, "tzinfo") and scheduled_at.tzinfo is None:
        from django.utils.timezone import make_aware
        scheduled_at = make_aware(scheduled_at)

    if scheduled_at <= now:
        raise ValidationError(
            f"Scheduled publish time must be in the future. "
            f"Provided: {scheduled_at.isoformat()} — Current time: {now.isoformat()}"
        )


def validate_publish_schedule_minimum_advance(
    scheduled_at, minimum_minutes: int = 5
) -> None:
    """
    Validate that a publish schedule is at least N minutes in the future.

    Prevents scheduling content to publish immediately (Celery needs time
    to pick up the task).

    Args:
        scheduled_at: Target publish datetime.
        minimum_minutes: Minimum advance window in minutes (default 5).

    Raises:
        ValidationError: If the scheduled time is too soon.
    """
    if not scheduled_at:
        return

    now = timezone.now()
    if hasattr(scheduled_at, "tzinfo") and scheduled_at.tzinfo is None:
        from django.utils.timezone import make_aware
        scheduled_at = make_aware(scheduled_at)

    delta = (scheduled_at - now).total_seconds() / 60
    if delta < minimum_minutes:
        raise ValidationError(
            f"Publish must be scheduled at least {minimum_minutes} minutes in the future "
            f"to allow the job queue to process it. "
            f"Provided time is only {delta:.1f} minutes from now."
        )


def validate_no_duplicate_schedule(content_type: str, content_id, exclude_status: str = "cancelled") -> None:
    """
    Reject scheduling if a pending schedule already exists for the same content.

    Args:
        content_type: "article", "blog", or "page".
        content_id: UUID of the content record.
        exclude_status: Status to exclude from the check (default "cancelled").

    Raises:
        ValidationError: If a pending schedule already exists.
    """
    from apps.cms.models import PublishSchedule
    exists = PublishSchedule.objects.filter(
        content_type=content_type,
        content_id=content_id,
        status="pending"
    ).exclude(status=exclude_status).exists()

    if exists:
        raise ValidationError(
            f"A pending publish schedule already exists for this {content_type}. "
            f"Cancel the existing schedule before creating a new one."
        )


def validate_published_at_not_future_for_immediate(published_at) -> None:
    """
    Validate that `published_at` is not a far-future date when publishing immediately.

    When using PublishService.publish_article(), the `published_at` is set to now().
    If a serializer accepts a manual `published_at` override, it must not be
    more than 1 minute in the future (clock skew tolerance).

    Args:
        published_at: Provided published_at datetime value.

    Raises:
        ValidationError: If published_at is more than 60 seconds in the future.
    """
    if not published_at:
        return

    now = timezone.now()
    if hasattr(published_at, "tzinfo") and published_at.tzinfo is None:
        from django.utils.timezone import make_aware
        published_at = make_aware(published_at)

    delta_seconds = (published_at - now).total_seconds()
    if delta_seconds > 60:
        raise ValidationError(
            f"published_at must not be more than 60 seconds in the future when publishing immediately. "
            f"Use the schedule endpoint to schedule future publication."
        )


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSITE VALIDATORS (bundle related checks for serializer convenience)
# ─────────────────────────────────────────────────────────────────────────────

def validate_article_slug_full(value: str, exclude_id=None) -> None:
    """
    Run all slug validators for an Article in one call.

    Checks: format → reserved → duplicate.

    Args:
        value: Slug string.
        exclude_id: Article UUID to exclude from uniqueness check (for PATCH).

    Raises:
        ValidationError: On first failing check.
    """
    validate_cms_slug(value)
    validate_no_reserved_url(value)
    validate_unique_article_slug(value, exclude_id=exclude_id)


def validate_page_slug_full(value: str, exclude_id=None) -> None:
    """
    Run all slug validators for a Page in one call.

    Args:
        value: Slug string.
        exclude_id: Page UUID to exclude from uniqueness check (for PATCH).

    Raises:
        ValidationError: On first failing check.
    """
    validate_cms_slug(value)
    validate_no_reserved_url(value)
    validate_unique_page_slug(value, exclude_id=exclude_id)


def validate_blog_slug_full(value: str, exclude_id=None) -> None:
    """
    Run all slug validators for a Blog in one call.

    Args:
        value: Slug string.
        exclude_id: Blog UUID to exclude from uniqueness check (for PATCH).

    Raises:
        ValidationError: On first failing check.
    """
    validate_cms_slug(value)
    validate_no_reserved_url(value)
    validate_unique_blog_slug(value, exclude_id=exclude_id)


def validate_seo_block_full(
    meta_title: Optional[str],
    meta_description: Optional[str],
    canonical_url: Optional[str] = None,
    og_image_url: Optional[str] = None,
) -> None:
    """
    Run all SEO metadata validators in one call.

    Useful for serializer.validate() methods that need to check the full
    SEO block together.

    Args:
        meta_title: SEO meta title (optional — only validated if provided).
        meta_description: SEO meta description (optional).
        canonical_url: Canonical URL (optional).
        og_image_url: OpenGraph image URL (optional).

    Raises:
        ValidationError: On first failing check.
    """
    if meta_title:
        validate_seo_meta_title(meta_title)
    if meta_description:
        validate_seo_meta_description(meta_description)
    if canonical_url:
        validate_canonical_url(canonical_url)
    if og_image_url:
        validate_og_image_url(og_image_url)


def validate_publish_schedule_full(
    content_type: str,
    content_id,
    scheduled_at,
    is_new: bool = True,
) -> None:
    """
    Run all publish schedule validators in one call.

    Checks: not past → minimum advance → no duplicate pending.

    Args:
        content_type: "article", "blog", or "page".
        content_id: UUID of the content record.
        scheduled_at: Target publish datetime.
        is_new: If True, also checks for duplicate pending schedule.

    Raises:
        ValidationError: On first failing check.
    """
    validate_publish_date_not_past(scheduled_at)
    validate_publish_schedule_minimum_advance(scheduled_at)
    if is_new:
        validate_no_duplicate_schedule(content_type, content_id)


def validate_media_file_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> None:
    """Checks if the file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower().strip(".")
    if allowed_extensions is None:
        allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp", "mp4", "mp3", "pdf", "docx", "txt"]
    if ext not in allowed_extensions:
        raise ValidationError(f"File extension '.{ext}' is not supported. Supported: {allowed_extensions}")


def validate_media_file_size(file_size_bytes: int, max_size_bytes: int = 50 * 1024 * 1024) -> None:
    """Checks if the file size does not exceed the maximum allowed size."""
    if file_size_bytes > max_size_bytes:
        raise ValidationError(f"File size exceeds the limit of {max_size_bytes} bytes.")


def validate_virus_free(file) -> None:
    """Simulates a virus scanner hook validation."""
    # Placeholder for actual antivirus integration
    pass
