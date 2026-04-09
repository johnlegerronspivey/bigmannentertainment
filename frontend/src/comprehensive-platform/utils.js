const API = process.env.REACT_APP_BACKEND_URL;

const handleApiError = (error, context) => {
  console.error(`Error in ${context}:`, error);
  
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }
  
  console.error('API Error:', error.response?.data?.message || error.message || 'Unknown error');
};

const handleApiResponse = (response, successCallback, errorMessage = 'API call failed') => {
  if (response?.data?.success) {
    if (successCallback) successCallback(response.data);
    return true;
  } else {
    console.error(errorMessage, response?.data?.message || 'Unknown error');
    return false;
  }
};

export { API, handleApiError, handleApiResponse };
