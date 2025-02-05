import axios from "axios";

const axiosInstance = axios.create({
	baseURL: "https://kind-ears-melt.loca.lt",
	withCredentials: true,
	headers: {  'Bypass-tunnel-reminder': true }
});

export default axiosInstance;
