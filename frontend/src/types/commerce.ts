export interface CartItem {
    sku?: string;
    title?: string;
    quantity: number;
    unit_price?: number;
    line_total: number;
}

export interface Cart {
    cart_id: string;
    items: CartItem[];
    item_count: number;
    total: number;
}

export interface OrderItem {
    sku?: string;
    title?: string;
    quantity: number;
    unit_price?: number;
    line_total: number;
}

export interface Order {
    order_id: string;
    status: string;
    payment_status: string;
    total_amount: number;
    items: OrderItem[];
    created_at?: string;
}

export interface OrderSummary {
    order_id: string;
    status: string;
    payment_status: string;
    total_amount: number;
    item_count: number;
    created_at?: string;
}
