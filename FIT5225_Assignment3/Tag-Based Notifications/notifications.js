// Notification management functions for the frontend

const API_ENDPOINT = 'https://your-api-gateway-url/dev'; // Replace with your actual API Gateway URL

class NotificationManager {
    constructor() {
        this.authToken = null; // Set this from your Cognito authentication
    }

    // Set the authentication token
    setAuthToken(token) {
        this.authToken = token;
    }

    // Subscribe to bird tags
    async subscribeToTags(tags) {
        try {
            const response = await fetch(`${API_ENDPOINT}/notifications/subscribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    operation: 'subscribe',
                    tags: tags
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Subscription failed');
            }

            return data;
        } catch (error) {
            console.error('Subscription error:', error);
            throw error;
        }
    }

    // Unsubscribe from bird tags
    async unsubscribeFromTags(tags = []) {
        try {
            const response = await fetch(`${API_ENDPOINT}/notifications/subscribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    operation: 'unsubscribe',
                    tags: tags // Empty array means unsubscribe from all
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Unsubscription failed');
            }

            return data;
        } catch (error) {
            console.error('Unsubscription error:', error);
            throw error;
        }
    }

    // List current subscriptions
    async listSubscriptions() {
        try {
            const response = await fetch(`${API_ENDPOINT}/notifications/subscribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    operation: 'list'
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to list subscriptions');
            }

            return data;
        } catch (error) {
            console.error('List subscriptions error:', error);
            throw error;
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
