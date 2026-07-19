# Scalability Strategy - BrahmaVidya Galaxy

## 1. Stateless Application Containers
- To scale out horizontally, application servers (Express/Django) are strictly stateless.
- Session structures are not held in server memory. Instead, they utilize secure JWT validations or distributed session stores (such as Redis cluster arrangements).
- Any server can handle any inbound request. Adding or removing containers has no impact on session state.

---

## 2. Database Read/Write Segregation
As Student enrollment grows, database read volume typically scales at a 10:1 ratio compared to writes. We decouple these pipelines to protect database write operations:

```
                  +--------------------------+
                  |  Load Balancer (Ingress) |
                  +--------------------------+
                                ||
         +----------------------+----------------------+
         ||                                            ||
         \/                                            \/
+------------------+                          +------------------+
| Write Server     |                          | Read Server      |
+------------------+                          +------------------+
         ||                                            ||
         \/ (Writes Only)                              \/ (Reads Only)
+------------------+                          +------------------+
| PostgreSQL Master| ===(Sync Replication)==> | Read Replicas    |
+------------------+                          +------------------+
```

- **PostgreSQL Master instance**: Dedicated solely to transaction commits, billing ledgers, state updates, and administrative edits.
- **Read Replicas**: Distribute data query loads (e.g., loading public pages, rendering course menus, displaying lesson content).

---

## 3. Background Job Workers & Message Queues
Heavy operations (such as compiling course statistics, generating certificate PDFs, executing complex AI operations, or dispatching global transactional emails) must be moved out of the main request thread to prevent request blocking:
- **Broker System**: Lightweight, secure queues (e.g., Redis, RabbitMQ, BullMQ, Celery) manage tasks.
- **Worker Clusters**: Isolated worker containers consume tasks asynchronously, keeping the main API gateway fast and responsive.

---

## 4. Horizontal Database Partitioning
When transactional data tables (e.g., `learning_progress` and `ledger_entries`) grow beyond 50 million records, database engines implement partitioning strategies:
- **Partition Keys**: Progress structures are partitioned by `user_id` or `course_id` hash ranges.
- **Archiving**: Closed financial ledger records are exported annually to compressed analytical cold-storage blocks, keeping active tables small and performant.
