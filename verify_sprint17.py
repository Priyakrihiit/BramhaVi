import os
import sys
import django

# Setup django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from apps.search.models import SearchIndex, SearchDocument
from apps.search.services import IndexService, RankingService
from apps.search.selectors import get_search_documents

def run_checks():
    print("==================================================")
    print("BrahmaVidya Search Platform Verification Script")
    print("==================================================")

    # 1. Verify indices count
    indices = SearchIndex.objects.all()
    print(f"[*] Found {indices.count()} Search Indexes:")
    for idx in indices:
        print(f"   - {idx.name}: {idx.description}")

    # 2. Verify indexed documents count
    docs = SearchDocument.objects.all()
    print(f"[*] Total indexed documents: {docs.count()}")

    # 3. Test dynamic index search selector
    print("[*] Testing query search selectors for keyword 'python'...")
    results = RankingService.apply_ranking(get_search_documents(), "python")
    print(f"    - Results count: {len(results)}")
    for doc in results[:3]:
        print(f"      * [{doc.index.name}] {doc.title} (Score: {doc.relevance_score})")

    # 4. Test Indexing a mock document
    print("[*] Creating mock index document...")
    doc = IndexService.index_document(
        index_name="testing",
        entity_type="MockItem",
        entity_id="999f1880-2a25-4a3b-8401-69095d9f9f17",
        title="Mock Verification Course item",
        excerpt="This is a test run entry.",
        body="Verification body contents for search platform test verification.",
        url_path="/test/verification-item"
    )
    print(f"    - Created mock doc ID: {doc.id}")

    # Clean up mock document
    IndexService.delete_document("MockItem", "999f1880-2a25-4a3b-8401-69095d9f9f17")
    print("    - Mock document cleaned up successfully.")
    
    print("\n[+] Verification checks completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    run_checks()
