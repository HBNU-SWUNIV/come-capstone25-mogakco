import { TokenManager } from '@/shared/utils/token';
import { useCallback } from 'react';

export const useToken = () => {
	const getAccessToken = useCallback(() => {
		return TokenManager.getAccessToken();
	}, []);

	const getRefreshToken = useCallback(() => {
		return TokenManager.getRefreshToken();
	}, []);

	const setTokens = useCallback((accessToken: string, refreshToken: string) => {
		TokenManager.setTokens(accessToken, refreshToken);
	}, []);

	const removeTokens = useCallback(() => {
		TokenManager.removeTokens();
	}, []);

	const hasTokens = useCallback(() => {
		return TokenManager.hasTokens();
	}, []);

	return {
		getAccessToken,
		getRefreshToken,
		setTokens,
		removeTokens,
		hasTokens,
	};
};
