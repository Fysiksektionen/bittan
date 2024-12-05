import axios from "axios";

const axiosInstance = axios.create({
	baseURL: "http://localhost:8000/",
	withCredentials: false,

});

export default axiosInstance;
