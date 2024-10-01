export const api = {
    host: () => {
        return `http://${window?.location.hostname || 'localhost'}:5000`
    }
}

export const ws = {
    host: () => {
        return `ws://${window?.location.hostname || 'localhost'}:5000`
    }
}

export default api;