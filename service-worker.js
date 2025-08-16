// service-worker.js

self.addEventListener('push', (event) => {
  const data = event.data.json();
  console.log('Push received:', data);

  const title = data.title || 'Website Automation Notification';
  const options = {
    body: data.body || 'A service status has changed.',
    icon: data.icon || 'https://raw.githubusercontent.com/RetailCloud/website-automation/main/icon.png', // Fallback icon
    badge: data.badge || 'https://raw.githubusercontent.com/RetailCloud/website-automation/main/icon.png',
    data: {
      url: data.url || self.registration.scope // URL to open when notification is clicked
    }
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const urlToOpen = event.notification.data.url;
  event.waitUntil(clients.openWindow(urlToOpen));
});

self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
  event.waitUntil(clients.claim());
});
