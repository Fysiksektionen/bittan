// src/notification.js
export const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        // Subscribe to backend for push notifications
      }
    }
  };
  