<<<<<<< HEAD
self.addEventListener('install', function(e) {
    e.waitUntil(
      caches.open('shariya-store').then(function(cache) {
        return cache.addAll([
          '/',
          '/?her=shariya143'
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', function(e) {
    e.respondWith(
      caches.match(e.request).then(function(response) {
        return response || fetch(e.request);
      })
    );
  });
=======
self.addEventListener('install', function(e) {
    e.waitUntil(
      caches.open('shariya-store').then(function(cache) {
        return cache.addAll([
          '/',
          '/?her=shariya143'
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', function(e) {
    e.respondWith(
      caches.match(e.request).then(function(response) {
        return response || fetch(e.request);
      })
    );
  });
>>>>>>> d3ad2b3662c719160932270b172cfcffc5e297e0
  