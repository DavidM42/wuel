'use strict';

// pulled from https://github.com/tretapey/svelte-pwa

// only used by subjects pages not by main courses list index.html
// still in this static folder to only be copied once

// Update cache names any time any of the cached files change.
const CACHE_NAME = 'static-cache-v1';

// inspired by https://stackoverflow.com/a/14462451
const path = window.location.pathname
const subjectPath = path.substr(0, path.lastIndexOf("/"));

// path where static assets for all reside in
const staticPath = subjectPath.substr(0, subjectPath.lastIndexOf("/")) + '/static';

// Add list of files to cache here.
const FILES_TO_CACHE = [
    `${subjectPath}/index.html`,
    `${subjectPath}/manifest.json`,
    `${subjectPath}/courses.json`,
    `${staticPath}/icons/favicon.ico`,
    `${staticPath}/main.css`,
    `${staticPath}/icons/favicon-96x96.png`,
    `${staticPath}/icons/favicon-16x16.png`,
    `${staticPath}/external/bootstrap.min.css`,
    `${staticPath}/external/bootstrap-native.min.js`
];

self.addEventListener('install', (evt) => {
    console.log('[ServiceWorker] Install');

    evt.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching offline page');
            return cache.addAll(FILES_TO_CACHE);
        })
    );

    self.skipWaiting();
});

self.addEventListener('activate', (evt) => {
    console.log('[ServiceWorker] Activate');
    // Remove previous cached data from disk.
    evt.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    console.log('[ServiceWorker] Removing old cache', key);
                    return caches.delete(key);
                }
            }));
        })
    );

    self.clients.claim();
});

self.addEventListener('fetch', (evt) => {
    console.log('[ServiceWorker] Fetch', evt.request.url);
    // Add fetch event handler here.
    if (evt.request.mode !== 'navigate') {
        // Not a page navigation, bail.
        return;
    }
    evt.respondWith(
        fetch(evt.request)
            .catch(() => {
                return caches.open(CACHE_NAME)
                    .then((cache) => {
                        return cache.match('index.html');
                    });
            })
    );
});