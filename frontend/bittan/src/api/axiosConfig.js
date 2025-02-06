import axios from "axios";

const axiosInstance = axios.create({
	baseURL: import.meta.env.VITE_APPLICATION_API_URL,
	withCredentials: true,
	headers: {  'Bypass-tunnel-reminder': true }
});

export default axiosInstance;
