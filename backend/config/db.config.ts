// Backend Database Connection Pool - Placeholder
// Purpose: Establishes transactional pooling configurations.

export const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'brahmavidya',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
  max: 20, // Max clients in pool
  idleTimeoutMillis: 30000,
};
