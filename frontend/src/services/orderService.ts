import { apiClient } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { Order, OrderConfirmation, OrderSummary } from '@/types';

export const orderService = {
    async prepare(): Promise<OrderConfirmation> {
        const response = await apiClient.post<OrderConfirmation>(
            API_ENDPOINTS.ORDERS.PREPARE
        );
        return response.data;
    },

    async confirm(confirmationId: string): Promise<Order> {
        const response = await apiClient.post<Order>(API_ENDPOINTS.ORDERS.BASE, {
            confirmation_id: confirmationId,
        });
        return response.data;
    },

    async cancelPrepare(confirmationId: string): Promise<void> {
        await apiClient.delete(API_ENDPOINTS.ORDERS.CANCEL_PREPARE(confirmationId));
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
