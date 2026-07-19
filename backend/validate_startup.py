import os
import sys
import time
import psutil
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
import redis
import stripe

def run_validation():
    start_time = time.time()
    warnings = []
    failed_services = []
    connected_services = []
    
    # 1. Environment variables check
    required_vars = [
        "DJANGO_SECRET_KEY", "JWT_SECRET_KEY", "GEMINI_API_KEY", 
        "STRIPE_SECRET_KEY", "REDIS_URL"
    ]
    missing_vars = [v for v in required_vars if not os.getenv(v)]
    
    # 2. Database connectivity
    db_status = "OK"
    try:
        connection.ensure_connection()
        connected_services.append("Database")
    except Exception as e:
        db_status = "WARNING"
        failed_services.append("Database")
        warnings.append(f"Database connectivity failed: {str(e)}")
        
    # 3. Redis connectivity
    redis_status = "OK"
    redis_url = os.getenv("REDIS_URL") or "redis://127.0.0.1:6379/0"
    try:
        r = redis.Redis.from_url(redis_url, socket_timeout=2)
        r.ping()
        connected_services.append("Redis")
    except Exception as e:
        redis_status = "WARNING"
        failed_services.append("Redis")
        warnings.append(f"Redis connectivity failed: {str(e)}")
        
    # 4. Stripe configuration check
    stripe_status = "OK"
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_key or stripe_key == "mock_key":
        stripe_status = "WARNING"
        failed_services.append("Stripe")
        warnings.append("Stripe is running in mock mode (STRIPE_SECRET_KEY is missing or mock).")
    else:
        connected_services.append("Stripe")
        
    # 5. Gemini configuration check
    gemini_status = "OK"
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "MY_GEMINI_API_KEY":
        gemini_status = "WARNING"
        failed_services.append("Gemini")
        warnings.append("Gemini API key is missing or mock; AI Coach will use simulations.")
    else:
        connected_services.append("Gemini")
        
    # 6. Migration Status Check
    migration_status = "OK"
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            migration_status = "WARNING"
            warnings.append(f"There are {len(plan)} unapplied migrations.")
    except Exception as e:
        migration_status = "WARNING"
        warnings.append(f"Failed to load migration plan: {str(e)}")
        
    # 7. Write access to storage paths
    storage_status = "OK"
    for path_name, path_val in [("MEDIA_ROOT", settings.MEDIA_ROOT), ("STATIC_ROOT", settings.STATIC_ROOT)]:
        if path_val:
            try:
                if not os.path.exists(path_val):
                    os.makedirs(path_val, exist_ok=True)
                test_file = os.path.join(path_val, ".startup_check")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                storage_status = "WARNING"
                warnings.append(f"Storage path {path_name} ({path_val}) is not writable: {str(e)}")
                
    # Calculate Status
    app_status = "READY"
    if warnings:
        app_status = "READY WITH WARNINGS"
        
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    duration = time.time() - start_time
    
    # Print out report
    print("=" * 60)
    print("        BRAHMAVIDYA GALAXY STARTUP VALIDATION CHECK")
    print("=" * 60)
    print(f"Database          : {db_status}")
    print(f"Redis             : {redis_status}")
    print(f"Gemini            : {gemini_status}")
    print(f"Stripe            : {stripe_status}")
    print(f"Storage           : {storage_status}")
    print(f"Migrations        : {migration_status}")
    print("-" * 60)
    print(f"Application Status: {app_status}")
    print("=" * 60)
    
    print("\n[STARTUP REPORT]")
    print(f"Startup Time      : {duration:.4f} seconds")
    print(f"Memory Usage      : {memory_usage_mb:.2f} MB")
    print(f"Missing Env Vars  : {', '.join(missing_vars) if missing_vars else 'None'}")
    print(f"Connected Services: {', '.join(connected_services)}")
    print(f"Failed Services   : {', '.join(failed_services)}")
    
    if warnings:
        print("\n[WARNINGS]")
        for w in warnings:
            print(f" - {w}")
            
    print("=" * 60)

if __name__ == "__main__":
    run_validation()
