'use client';

import React, { useEffect } from 'react';
import { Badge, Button, Card, Separator, Sheet, SheetContent, Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui';
import { useCartStore } from '@/store';
import { CheckCircle2, Minus, Plus, ShoppingBag, Trash2 } from 'lucide-react';

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

    const items = cart?.items ?? [];
    const reviewItems = pendingConfirmation?.items ?? [];

    return (
        <Sheet open={isOpen} onOpenChange={(open) => !open && closeDrawer()}>
            <SheetContent className="flex flex-col p-0" side="right">
                <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
                    <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Your Pharmacy</p>
                        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                            Cart & Orders
                        </h2>
                    </div>
                    <Button variant="ghost" size="sm" onClick={closeDrawer} aria-label="Close drawer">
                        ✕
                    </Button>
                </div>

                <div className="border-b border-slate-200 p-4 dark:border-slate-800">
                    <Tabs value={activeTab} onValueChange={(value) => setTab(value as 'cart' | 'orders')}>
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="cart">Cart ({cart?.item_count ?? 0})</TabsTrigger>
                            <TabsTrigger value="orders">Orders</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>

                {error && (
                    <div className="mx-4 mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 dark:border-red-900/40 dark:bg-red-950/20">
                        <div className="flex items-center justify-between gap-3">
                            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                            <Button variant="ghost" size="sm" onClick={clearError}>
                                ✕
                            </Button>
                        </div>
                    </div>
                )}

                <Tabs value={activeTab} onValueChange={(value) => setTab(value as 'cart' | 'orders')} className="flex min-h-0 flex-1 flex-col">
                    <TabsContent value="cart" className="flex min-h-0 flex-1 flex-col">
                        <div className="flex-1 space-y-3 overflow-y-auto p-4">
                            {checkoutStep === 'cart' && items.length === 0 && !isLoading && (
                                <div className="mt-10 flex flex-col items-center justify-center gap-2 text-center text-slate-500">
                                    <ShoppingBag className="h-8 w-8 text-slate-400" />
                                    <p className="text-sm">Your cart is empty.</p>
                                </div>
                            )}

                            {checkoutStep === 'cart' &&
                                items.map((item) => (
                                    <Card key={item.sku} className="rounded-xl p-3">
                                        <div className="flex items-start gap-3">
                                            <div className="min-w-0 flex-1">
                                                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                                                    {item.title || item.sku}
                                                </p>
                                                <p className="mt-0.5 text-xs text-slate-500">
                                                    ₹{item.unit_price ?? 0} each
                                                </p>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => removeItem(item.sku!)}
                                                disabled={isLoading}
                                                aria-label="Remove item"
                                            >
                                                <Trash2 className="h-4 w-4 text-slate-500" />
                                            </Button>
                                        </div>
                                        <Separator className="my-3" />
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => updateItem(item.sku!, Math.max(0, item.quantity - 1))}
                                                    disabled={isLoading}
                                                >
                                                    <Minus className="h-3.5 w-3.5" />
                                                </Button>
                                                <span className="w-8 text-center text-sm font-medium text-slate-900 dark:text-slate-100">
                                                    {item.quantity}
                                                </span>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => updateItem(item.sku!, item.quantity + 1)}
                                                    disabled={isLoading}
                                                >
                                                    <Plus className="h-3.5 w-3.5" />
                                                </Button>
                                            </div>
                                            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                                                ₹{item.line_total}
                                            </p>
                                        </div>
                                    </Card>
                                ))}

                            {checkoutStep === 'review' && (
                                <Card className="rounded-xl border-blue-200 bg-blue-50 p-3 dark:border-blue-900/40 dark:bg-blue-950/20">
                                    <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">
                                        Review your order before placing
                                    </p>
                                    <p className="mt-1 text-xs text-blue-600 dark:text-blue-300/90">
                                        Confirmation expires at {formatDate(pendingConfirmation?.expires_at)}
                                    </p>
                                </Card>
                            )}

                            {checkoutStep === 'review' &&
                                reviewItems.map((item) => (
                                    <Card key={item.sku} className="rounded-xl p-3">
                                        <div className="flex items-center justify-between gap-3">
                                            <div className="min-w-0 flex-1">
                                                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                                                    {item.title || item.sku}
                                                </p>
                                                <p className="mt-0.5 text-xs text-slate-500">
                                                    ₹{item.unit_price ?? 0} each
                                                </p>
                                            </div>
                                            <Badge variant="secondary">x {item.quantity}</Badge>
                                            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                                                ₹{item.line_total}
                                            </p>
                                        </div>
                                    </Card>
                                ))}
                        </div>

                        {checkoutStep === 'cart' && items.length > 0 && (
                            <div className="border-t border-slate-200 p-4 dark:border-slate-800">
                                <div className="mb-3 flex items-center justify-between text-sm font-semibold text-slate-900 dark:text-slate-100">
                                    <span>Total</span>
                                    <span>₹{cart?.total ?? 0}</span>
                                </div>
                                <Button className="w-full" onClick={() => prepareCheckout()} disabled={isLoading}>
                                    {isLoading ? 'Preparing review...' : 'Proceed to review'}
                                </Button>
                            </div>
                        )}

                        {checkoutStep === 'review' && (
                            <div className="space-y-3 border-t border-slate-200 p-4 dark:border-slate-800">
                                <div className="flex items-center justify-between text-sm font-semibold text-slate-900 dark:text-slate-100">
                                    <span>Total</span>
                                    <span>₹{pendingConfirmation?.total ?? 0}</span>
                                </div>
                                <Button className="w-full" onClick={() => confirmCheckout()} disabled={isLoading}>
                                    {isLoading ? 'Placing order...' : 'Confirm & place order'}
                                </Button>
                                <div className="grid grid-cols-2 gap-2">
                                    <Button variant="secondary" className="w-full" onClick={() => backToCart()} disabled={isLoading}>
                                        Back to cart
                                    </Button>
                                    <Button variant="danger" className="w-full" onClick={() => cancelCheckout()} disabled={isLoading}>
                                        Cancel review
                                    </Button>
                                </div>
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="orders" className="flex min-h-0 flex-1 flex-col">
                        <div className="flex-1 space-y-3 overflow-y-auto p-4">
                            {lastOrder && (
                                <Card className="rounded-xl border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-900/40 dark:bg-emerald-950/20">
                                    <div className="flex items-center gap-2">
                                        <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-300" />
                                        <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
                                            Order placed successfully
                                        </p>
                                    </div>
                                    <p className="mt-1 text-xs text-emerald-700/90 dark:text-emerald-300/90">
                                        #{lastOrder.order_id.slice(0, 8)} · ₹{lastOrder.total_amount}
                                    </p>
                                </Card>
                            )}

                            {orders.length === 0 && !isLoading && (
                                <p className="mt-10 text-center text-sm text-slate-500">No orders yet.</p>
                            )}

                            {orders.map((order) => (
                                <Card key={order.order_id} className="rounded-xl p-3">
                                    <div className="flex items-center justify-between gap-2">
                                        <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                                            #{order.order_id.slice(0, 8)}
                                        </p>
                                        <Badge variant="outline" className="capitalize">
                                            {order.status}
                                        </Badge>
                                    </div>
                                    <p className="mt-2 text-xs text-slate-500">
                                        {order.item_count} item(s) · {formatDate(order.created_at)}
                                    </p>
                                    <div className="mt-2 flex items-center justify-between">
                                        <p className="text-xs capitalize text-slate-500">
                                            Payment: {order.payment_status.replace('_', ' ')}
                                        </p>
                                        <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                                            ₹{order.total_amount}
                                        </p>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </TabsContent>
                </Tabs>
            </SheetContent>
        </Sheet>
    );
};
