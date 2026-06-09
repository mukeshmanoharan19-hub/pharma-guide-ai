import { create } from 'zustand';
import { Cart, Order, OrderSummary } from '@/types';
import { cartService, orderService } from '@/services';

interface CartStore {
    cart: Cart | null;
    orders: OrderSummary[];
    lastOrder: Order | null;
    isOpen: boolean;
    activeTab: 'cart' | 'orders';
    isLoading: boolean;
    error: string | null;

    openDrawer: (tab?: 'cart' | 'orders') => void;
    closeDrawer: () => void;
    setTab: (tab: 'cart' | 'orders') => void;
    clearError: () => void;

    fetchCart: () => Promise<void>;
    addItem: (sku: string, quantity?: number) => Promise<void>;
    updateItem: (sku: string, quantity: number) => Promise<void>;
    removeItem: (sku: string) => Promise<void>;
    checkout: () => Promise<Order | null>;
    fetchOrders: () => Promise<void>;
}

const extractError = (error: any, fallback: string) =>
    error?.response?.data?.detail || error?.message || fallback;

export const useCartStore = create<CartStore>((set, get) => ({
    cart: null,
    orders: [],
    lastOrder: null,
    isOpen: false,
    activeTab: 'cart',
    isLoading: false,
    error: null,

    openDrawer: (tab) => {
        set({ isOpen: true, ...(tab ? { activeTab: tab } : {}) });
        if (tab === 'orders') {
            get().fetchOrders();
        } else {
            get().fetchCart();
        }
    },
    closeDrawer: () => set({ isOpen: false }),
    setTab: (activeTab) => {
        set({ activeTab });
        if (activeTab === 'orders') get().fetchOrders();
        else get().fetchCart();
    },
    clearError: () => set({ error: null }),

    fetchCart: async () => {
        set({ isLoading: true, error: null });
        try {
            const cart = await cartService.get();
            set({ cart, isLoading: false });
        } catch (error: any) {
            set({ error: extractError(error, 'Failed to load cart'), isLoading: false });
        }
    },

    addItem: async (sku, quantity = 1) => {
        set({ isLoading: true, error: null });
        try {
            const cart = await cartService.addItem(sku, quantity);
            set({ cart, isLoading: false, isOpen: true, activeTab: 'cart' });
        } catch (error: any) {
            set({ error: extractError(error, 'Failed to add item'), isLoading: false });
        }
    },

    updateItem: async (sku, quantity) => {
        set({ isLoading: true, error: null });
        try {
            const cart = await cartService.updateItem(sku, quantity);
            set({ cart, isLoading: false });
        } catch (error: any) {
            set({ error: extractError(error, 'Failed to update item'), isLoading: false });
        }
    },

    removeItem: async (sku) => {
        set({ isLoading: true, error: null });
        try {
            const cart = await cartService.removeItem(sku);
            set({ cart, isLoading: false });
        } catch (error: any) {
            set({ error: extractError(error, 'Failed to remove item'), isLoading: false });
        }
    },

    checkout: async () => {
        set({ isLoading: true, error: null });
        try {
            const order = await orderService.create();
            // Refresh cart (now empty) and order history.
            const cart = await cartService.get();
            set({ lastOrder: order, cart, isLoading: false, activeTab: 'orders' });
            await get().fetchOrders();
            return order;
        } catch (error: any) {
            set({ error: extractError(error, 'Checkout failed'), isLoading: false });
            return null;
        }
    },

    fetchOrders: async () => {
        set({ isLoading: true, error: null });
        try {
            const orders = await orderService.list();
            set({ orders, isLoading: false });
        } catch (error: any) {
            set({ error: extractError(error, 'Failed to load orders'), isLoading: false });
        }
    },
}));
