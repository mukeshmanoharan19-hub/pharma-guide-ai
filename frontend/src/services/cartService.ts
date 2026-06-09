import { apiClient } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { Cart } from '@/types';

export const cartService = {
    async get(): Promise<Cart> {
        const response = await apiClient.get<Cart>(API_ENDPOINTS.CART.BASE);
        return response.data;
    },

    async addItem(sku: string, quantity = 1): Promise<Cart> {
        const response = await apiClient.post<Cart>(API_ENDPOINTS.CART.ITEMS, {
            sku,
            quantity,
        });
        return response.data;
    },

    async updateItem(sku: string, quantity: number): Promise<Cart> {
        const response = await apiClient
            .getClient()
            .patch<Cart>(API_ENDPOINTS.CART.ITEM(sku), { quantity });
        return response.data;
    },

    async removeItem(sku: string): Promise<Cart> {
        const response = await apiClient.delete<Cart>(API_ENDPOINTS.CART.ITEM(sku));
        return response.data;
    },
};
