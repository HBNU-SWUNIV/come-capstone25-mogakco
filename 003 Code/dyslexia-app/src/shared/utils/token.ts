const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
// Backward-compat keys used elsewhere in the app
const ACCESS_TOKEN_KEY_CAMEL = 'accessToken';
const REFRESH_TOKEN_KEY_CAMEL = 'refreshToken';

export class TokenManager {
	static getAccessToken(): string | null {
		const token = localStorage.getItem(ACCESS_TOKEN_KEY);
		if (token) return token;
		// Fallback to legacy key
		return localStorage.getItem(ACCESS_TOKEN_KEY_CAMEL);
	}

	static getRefreshToken(): string | null {
		const token = localStorage.getItem(REFRESH_TOKEN_KEY);
		if (token) return token;
		// Fallback to legacy key
		return localStorage.getItem(REFRESH_TOKEN_KEY_CAMEL);
	}

	static setTokens(accessToken: string, refreshToken: string): void {
		// Store under both snake_case and camelCase for compatibility
		localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
		localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
		localStorage.setItem(ACCESS_TOKEN_KEY_CAMEL, accessToken);
		localStorage.setItem(REFRESH_TOKEN_KEY_CAMEL, refreshToken);
	}

	static removeTokens(): void {
		localStorage.removeItem(ACCESS_TOKEN_KEY);
		localStorage.removeItem(REFRESH_TOKEN_KEY);
		localStorage.removeItem(ACCESS_TOKEN_KEY_CAMEL);
		localStorage.removeItem(REFRESH_TOKEN_KEY_CAMEL);
	}

	static hasTokens(): boolean {
		return !!TokenManager.getAccessToken() && !!TokenManager.getRefreshToken();
	}
}
