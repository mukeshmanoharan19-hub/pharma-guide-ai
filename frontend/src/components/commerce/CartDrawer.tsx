'use client';

import React, { useEffect } from 'react';
import { Button } from '@/components/ui';
import { useCartStore } from '@/store';

const formatDate = (iso?: string) =>
    iso ? new Date(iso).toLocaleString() : '';

export const CartDrawer: React.FC = () => {
    const {
        cart,
        orders,
        lastOrder,
        pendingConfirmation,
        checkoutStep,
        isOpen,
        activeTab,
        isLoading,
        error,
        closeDrawer,
        setTab,
        clearError,
        fetchCart,
        updateItem,
        removeItem,
        prepareCheckout,
        confirmCheckout,
        cancelCheckout,
        backToCart,
    } = useCartStore();

    useEffect(() => {
        if (isOpen && activeTab === 'cart') {
            fetchCart();
        }
    }, [isOpen, activeTab, fetchCart]);

    if (!isOpen) return null;

    const items = cart?.items ?? [];
    const reviewItems = pendingConfirmation?.items ?? [];

    return (
        <div className="fixed inset-0 z-50 flex justify-end">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/40"
                onClick={closeDrawer}
                aria-hidden
            />

            {/* Panel */}
            <div className="relative w-full max-w-md h-full bg-white shadow-xl flex flex-col">
                <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-cyan-500">
                    <h2 className="text-lg font-bold text-white">Your Pharmacy</h2>
                    <button
                        onClick={closeDrawer}
                        className="text-white hover:text-gray-200 text-xl"
                        aria-label="Close"
                    >
                        ✕
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200">
                    {(['cart', 'orders'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setTab(tab)}
                            className={`flex-1 py-3 text-sm font-medium capitalize transition-colors ${
                                activeTab === tab
                                    ? 'text-blue-600 border-b-2 border-blue-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            {tab === 'cart' ? `Cart (${cart?.item_count ?? 0})` : 'Orders'}
                        </button>
                    ))}
                </div>

                {error && (
                    <div className="p-3 bg-red-50 border-b border-red-200 flex justify-between">
                        <p className="text-sm text-red-600">{error}</p>
                        <button onClick={clearError} className="text-red-500 font-semibold">
                            ✕
                        </button>
                    </div>
                )}

                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {activeTab === 'cart' && checkoutStep === 'cart' && (
                        <>
                            {items.length === 0 && !isLoading && (
                                <p className="text-center text-gray-400 mt-8">
                                    Your cart is empty.
                                </p>
                            )}
                            {items.map((item) => (
                                <div
                                    key={item.sku}
                                    className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg"
                                >
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 text-sm">
                                            {item.title || item.sku}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            ₹{item.unit_price ?? 0} each
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            className="w-7 h-7 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                                            onClick={() =>
                                                updateItem(item.sku!, Math.max(0, item.quantity - 1))
                                            }
                                            disabled={isLoading}
                                        >
                                            −
                                        </button>
                                        <span className="w-6 text-center text-sm">
                                            {item.quantity}
                                        </span>
                                        <button
                                            className="w-7 h-7 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                                            onClick={() => updateItem(item.sku!, item.quantity + 1)}
                                            disabled={isLoading}
                                        >
                                            +
                                        </button>
                                    </div>
                                    <div className="w-16 text-right text-sm font-semibold text-blue-600">
                                        ₹{item.line_total}
                                    </div>
                                    <button
                                        onClick={() => removeItem(item.sku!)}
                                        className="text-gray-400 hover:text-red-500"
                                        aria-label="Remove"
                                        disabled={isLoading}
                                    >
                                        🗑
                                    </button>
                                </div>
                            ))}
                        </>
                    )}

                    {activeTab === 'cart' && checkoutStep === 'review' && (
                        <>
                            <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                                <p className="text-sm font-semibold text-blue-700">
                                    Review your order before placing
                                </p>
                                <p className="text-xs text-blue-600 mt-1">
                                    Confirmation expires at {formatDate(pendingConfirmation?.expires_at)}
                                </p>
                            </div>
                            {reviewItems.map((item) => (
                                <div
                                    key={item.sku}
                                    className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg bg-gray-50"
                                >
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 text-sm">
                                            {item.title || item.sku}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            ₹{item.unit_price ?? 0} each
                                        </p>
                                    </div>
                                    <span className="text-sm text-gray-700">
                                        x {item.quantity}
                                    </span>
                                    <span className="w-16 text-right text-sm font-semibold text-blue-600">
                                        ₹{item.line_total}
                                    </span>
                                </div>
                            ))}
                        </>
                    )}

                    {activeTab === 'orders' && (
                        <>
                            {lastOrder && (
                                <div className="p-3 rounded-lg bg-green-50 border border-green-200 mb-2">
                                    <p className="text-sm font-semibold text-green-700">
                                        Order placed! ✅
                                    </p>
                                    <p className="text-xs text-green-600">
                                        #{lastOrder.order_id.slice(0, 8)} · ₹{lastOrder.total_amount}
                                    </p>
                                </div>
                            )}
                            {orders.length === 0 && !isLoading && (
                                <p className="text-center text-gray-400 mt-8">No orders yet.</p>
                            )}
                            {orders.map((order) => (
                                <div
                                    key={order.order_id}
                                    className="p-3 border border-gray-200 rounded-lg"
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-medium text-gray-900">
                                            #{order.order_id.slice(0, 8)}
                                        </span>
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 capitalize">
                                            {order.status}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center mt-1">
                                        <span className="text-xs text-gray-500">
                                            {order.item_count} item(s) · {formatDate(order.created_at)}
                                        </span>
                                        <span className="text-sm font-semibold text-blue-600">
                                            ₹{order.total_amount}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-400 mt-1 capitalize">
                                        Payment: {order.payment_status.replace('_', ' ')}
                                    </p>
                                </div>
                            ))}
                        </>
                    )}
                </div>

                {/* Footer / checkout */}
                {activeTab === 'cart' && checkoutStep === 'cart' && items.length > 0 && (
                    <div className="border-t border-gray-200 p-4 space-y-3">
                        <div className="flex justify-between font-semibold text-gray-900">
                            <span>Total</span>
                            <span>₹{cart?.total ?? 0}</span>
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => prepareCheckout()}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Preparing review…' : 'Proceed to review'}
                        </Button>
                    </div>
                )}

                {activeTab === 'cart' && checkoutStep === 'review' && (
                    <div className="border-t border-gray-200 p-4 space-y-3">
                        <div className="flex justify-between font-semibold text-gray-900">
                            <span>Total</span>
                            <span>₹{pendingConfirmation?.total ?? 0}</span>
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => confirmCheckout()}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Placing order…' : 'Confirm & place order'}
                        </Button>
                        <div className="grid grid-cols-2 gap-2">
                            <Button
                                variant="secondary"
                                className="w-full"
                                onClick={() => backToCart()}
                                disabled={isLoading}
                            >
                                Back to cart
                            </Button>
                            <Button
                                variant="danger"
                                className="w-full"
                                onClick={() => cancelCheckout()}
                                disabled={isLoading}
                            >
                                Cancel review
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
