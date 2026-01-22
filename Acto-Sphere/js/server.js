const express = require('express');
const { createClient } = require('redis');
const path = require('path');
const app = express();
const PORT = 3000;

// Setup Redis Client
const redisUrl = process.env.REDIS_URL || 'redis://redis:6379';
const redisClient = createClient({ url: redisUrl });

redisClient.on('error', (err) => console.log('Redis Client Error', err));

(async () => {
    try {
        await redisClient.connect();
        console.log("Connected to Redis");
    } catch (e) {
        console.log("Redis Connection Failed (Offline Mode)", e);
    }
})();

app.use(express.static('public'));

app.get('/api/stats', async (req, res) => {
    try {
        if (!redisClient.isOpen) {
             throw new Error("Redis not ready");
        }

        // Fetch directly from RAM (Cache)
        const stats = await redisClient.get('dashboard_stats');
        
        if (stats) {
            const data = JSON.parse(stats);
            // Add mock weather since Rust engine doesn't calculate it yet
            data.weather = { 
                location: "Server Farm", 
                temperature_c: 24, 
                condition: "Optimal", 
                humidity_percent: 45 
            };
            res.json(data);
        } else {
            res.json({ status: "warming_up" });
        }
    } catch (err) {
        console.error("Cache Miss/Error:", err.message);
        // Fallback or empty
        res.json({ frequent_analytics: {}, status: "cache_miss" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/dashboard.html`);
});