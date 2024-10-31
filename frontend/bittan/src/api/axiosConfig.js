import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost/backend',
  withCredentials: true,
});

export default axiosInstance;
