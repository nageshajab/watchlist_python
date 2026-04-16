self.addEventListener("install", (e) => {
  console.log("Service Worker: Installed");
});

self.addEventListener("fetch", (e) => {
  // This can be empty, but it must exist for the install prompt to trigger
  e.respondWith(fetch(e.request));
});
