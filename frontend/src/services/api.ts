// API Client Service Brokers - Placeholder
// Purpose: Outlines REST network channels targeting backend resource parameters.

export const apiFetch = async (endpoint: string, options: any = {}) => {
  const response = await fetch(`/api/v1${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return response.json();
};
