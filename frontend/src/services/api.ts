import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_BASE_URL, APP_CONFIG } from '@/utils/constants';
import { tokenStorage } from '@/utils/tokenStorage';

class ApiClient {
    private client: AxiosInstance;
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL,
            timeout: APP_CONFIG.REQUEST_TIMEOUT,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Add interceptor to include token in requests
        this.client.interceptors.request.use((config) => {
            const token = tokenStorage.getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // Add error interceptor
        this.client.interceptors.response.use(
            (response) => response,
            (error: AxiosError) => {
                if (error.response?.status === 401) {
                    // Token expired or invalid
                    tokenStorage.delete();
                    window.location.href = '/auth/login';
                }
                return Promise.reject(error);
            }
        );
    }

    getClient(): AxiosInstance {
        return this.client;
    }

    setBaseURL(newURL: string) {
        this.baseURL = newURL;
        this.client = axios.create({
            baseURL: newURL,
            timeout: APP_CONFIG.REQUEST_TIMEOUT,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    async get<T>(url: string, config = {}) {
        return this.client.get<T>(url, config);
    }

    async post<T>(url: string, data?: any, config = {}) {
        return this.client.post<T>(url, data, config);
    }

    async put<T>(url: string, data?: any, config = {}) {
        return this.client.put<T>(url, data, config);
    }

    async delete<T>(url: string, config = {}) {
        return this.client.delete<T>(url, config);
    }
}

export const apiClient = new ApiClient();
