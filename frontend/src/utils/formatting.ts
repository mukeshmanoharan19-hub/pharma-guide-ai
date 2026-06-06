export const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
    });
};

export const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
};

export const scrollToBottom = (element: HTMLElement | null) => {
    if (element) {
        setTimeout(() => {
            element.scrollTop = element.scrollHeight;
        }, 0);
    }
};
