# CMS Performance Review

## 1. Database Query Optimizations
- **N+1 Prevention**: ViewSets utilize `select_related` and `prefetch_related` on ForeignKey and ManyToMany relations.
- **Index Tuning**: Primary keys use UUIDs. Foreign keys use index markers.
- **Selective Serializers**: Serializer outputs exclude unnecessary nested detail payloads when compiling listing arrays.

## 2. In-Memory Caching
- Dynamic menu tree compiling cache results under the `"global_navigation_menu_tree"` cache key.
- Save signal invalidations auto-clear cache keys upon content modifications.
