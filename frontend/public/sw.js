/* Video Studio service worker — minimal installability shim.
   No caching: every request passes straight through to the network. */
const VERSION = "vs-pwa-v1";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // Offline: let the browser show its default offline page.
      return Response.error();
    })
  );
});
