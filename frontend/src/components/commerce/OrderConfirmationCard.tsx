'use client';

import React, { useMemo, useState } from 'react';
import { Button } from '@/components/ui';
import { OrderConfirmation } from '@/types';
import { orderService } from '@/services';
import { useCartStore } from '@/store';

interface Props {
    confirmation: OrderConfirmation;
}

export const OrderConfirmationCard: React.FC<Props> = ({ confirmation }) => {
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [error, setError] = useState<string | null>(null);
    const [cancelled, setCancelled] = useState(false);
    const fetchCart = useCartStore((s) => s.fetchCart);
    const fetchOrders = useCartStore((s) => s.fetchOrders);

    const expired = useMemo(
        () => new Date(confirmation.expires_at).getTime() <= Date.now(),
        [confirmation.expires_at]
    );

    const handleConfirm = async () => {
        if (expired) {
            setError('This confirmation expired. Please request checkout review again.');
            setStatus('error');
            return;
        }
        setStatus('loading');
        setError(null);
        try {
            await orderService.confirm(confirmation.confirmation_id);
            await fetchCart();
            await fetchOrders();
            setStatus('success');
        } catch (e: any) {
            setError(e?.response?.data?.detail || e?.message || 'Failed to confirm order');
            setStatus('error');
        }
    };

    const handleCancel = async () => {
        try {
            await orderService.cancelPrepare(confirmation.confirmation_id);
        } catch {
            // Already cancelled/expired is fine.
        }
        setCancelled(true);
    };

    return (
        <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3">
            <p className="text-sm font-semibold text-blue-800">
                Order review required before placement
            </p>
            <p className="text-xs text-blue-700 mt-1">
                Confirmation ID: {confirmation.confirmation_id.slice(0, 8)} · Expires:{' '}
                {new Date(confirmation.expires_at).toLocaleString()}
            </p>

            <div className="mt-3 space-y-2">
                {confirmation.items.map((item) => (
                    <div key={`${confirmation.confirmation_id}-${item.sku}`} className="flex justify-between text-sm">
                        <span className="text-gray-700">
                            {item.title || item.sku} x {item.quantity}
                        </span>
                        <span className="font-medium text-gray-900">₹{item.line_total}</span>
                    </div>
                ))}
            </div>

            <div className="mt-3 flex justify-between font-semibold text-gray-900 text-sm">
                <span>Total</span>
                <span>₹{confirmation.total}</span>
            </div>

            {status === 'success' && (
                <p className="mt-2 text-sm text-green-700">Order confirmed and placed.</p>
            )}
            {cancelled && (
                <p className="mt-2 text-sm text-gray-600">Checkout confirmation cancelled.</p>
            )}
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

            <div className="mt-3 grid grid-cols-2 gap-2">
                <Button
                    className="w-full"
                    onClick={handleConfirm}
                    disabled={status === 'loading' || status === 'success' || cancelled}
                >
                    {status === 'loading' ? 'Placing...' : 'Confirm order'}
                </Button>
                <Button
                    variant="secondary"
                    className="w-full"
                    onClick={handleCancel}
                    disabled={status === 'loading' || status === 'success' || cancelled}
                >
                    Cancel
                </Button>
            </div>
        </div>
    );
};
