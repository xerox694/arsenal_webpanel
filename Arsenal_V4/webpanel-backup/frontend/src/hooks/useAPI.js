import { useState, useEffect } from 'react';

// Configuration API
const API_BASE_URL = 'http://localhost:5000/api';

// Hook pour les appels API génériques
export const useAPI = (endpoint, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          credentials: 'include', // Inclure les cookies de session
          headers: {
            'Content-Type': 'application/json',
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
        console.error(`API Error (${endpoint}):`, err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error, refetch: () => fetchData() };
};

// Hook spécifique pour l'authentification
export const useAuth = () => {
  const { data, loading, error } = useAPI('/auth/user');
  
  return {
    user: data,
    isAuthenticated: !!data?.authenticated,
    loading,
    error
  };
};

// Hook pour les statistiques
export const useStats = () => {
  const { data, loading, error } = useAPI('/stats');
  
  return {
    stats: data,
    loading,
    error
  };
};

// Hook pour les serveurs
export const useServers = () => {
  const { data, loading, error } = useAPI('/servers/list');
  
  return {
    servers: data?.servers || [],
    loading,
    error
  };
};

// Hook pour le profil utilisateur
export const useUserProfile = () => {
  const { data, loading, error } = useAPI('/user/profile');
  
  return {
    profile: data,
    loading,
    error
  };
};

// Hook pour les permissions utilisateur
export const useUserPermissions = () => {
  const { data, loading, error } = useAPI('/user/permissions');
  
  return {
    permissions: data,
    loading,
    error
  };
};

// Fonction utilitaire pour POST requests
export const apiPost = async (endpoint, postData) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API POST Error (${endpoint}):`, error);
    throw error;
  }
};

// Fonction utilitaire pour DELETE requests
export const apiDelete = async (endpoint) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API DELETE Error (${endpoint}):`, error);
    throw error;
  }
};
