// User Model Scheme - Placeholder
// Purpose: Database schema and index configurations for dynamic RBAC users.

export interface UserEntity {
  id: string;
  email: string;
  passwordHash: string;
  roleId: string;
  status: 'ACTIVE' | 'PENDING' | 'SUSPENDED';
  createdAt: string;
}
