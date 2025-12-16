import { TokenManager } from '@/shared/utils/token';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const axiosClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		'Content-Type': 'application/json',
	},
});

axiosClient.interceptors.request.use(
	(config) => {
		const token = TokenManager.getAccessToken();
		if (token) {
			config.headers.Authorization = `Bearer ${token}`;
		}
		return config;
	},
	(error) => {
		return Promise.reject(error);
	},
);

axiosClient.interceptors.response.use(
	(response) => {
		return response.data;
	},
	async (error) => {
		const originalRequest = error.config;

		// 토큰 만료 처리
		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true;

			try {
				const refreshToken = TokenManager.getRefreshToken();
				const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
					refreshToken,
				});

				const { accessToken, refreshToken: newRefreshToken } = response.data;
				if (accessToken) {
					TokenManager.setTokens(
						accessToken,
						newRefreshToken ?? refreshToken ?? '',
					);
					originalRequest.headers.Authorization = `Bearer ${accessToken}`;
				}
				return axiosClient(originalRequest);
			} catch (refreshError) {
				TokenManager.removeTokens();
				window.location.href = '/auth';
				return Promise.reject(refreshError);
			}
		}

		return Promise.reject(error);
	},
);
