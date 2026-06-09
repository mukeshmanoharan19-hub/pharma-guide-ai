import { apiClient } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { Order, OrderSummary } from '@/types';

export const orderService = {
    async create(): Promise<Order> {
        const response = await apiClient.post<Order>(API_ENDPOINTS.ORDERS.BASE, {
            confirm: true,
        });
        return response.data;
    },

    async list(): Promise<OrderSummary[]> {
        const response = await apiClient.get<OrderSummary[]>(
            API_ENDPOINTS.ORDERS.BASE
        );
        return response.data;
    },

    async track(orderId: string): Promise<Order> {
        const response = await apiClient.get<Order>(
            API_ENDPOINTS.ORDERS.TRACK(orderId)
        );
        return response.data;
    },
};
