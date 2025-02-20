import axios from "axios";

const axiosInstance = axios.create({
	baseURL: import.meta.env.VITE_APPLICATION_API_URL, // This is since the API is on another URL
	withCredentials: true,
	headers: {  'Bypass-tunnel-reminder': true } // Bypasses weird stuff with localtunnel
});

export default axiosInstance;
