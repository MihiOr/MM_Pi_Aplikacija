const express = require('express');
const fetch = require('node-fetch'); // node-fetch@2
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server); // 🔥

const PYTHON_API = 'http://localhost:8069';

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

io.on('connection', (socket) => {
    console.log('A client connected:', socket.id);

    socket.on('admin-alert', (msg) => {
        console.log(`🚨 Admin alert received: "${msg}", broadcasting to all clients`);
        io.emit('show-alert', msg);
    });
    socket.on('client-alert', (msg) => {
        console.log(`📩 Client ${socket.id} sent alert: ${msg}`);
        io.emit('show-client-alert', { msg, from: socket.id }); // 🔥 broadcast to all viewers (admin)
    });
});

app.post('/proxy/:endpoint', async (req, res) => {
    const { endpoint } = req.params;
    const requestLog = {
        time: new Date().toLocaleTimeString(),
        endpoint: endpoint,
        body: req.body
    };

    // 🔥 Emit to server.html
    io.emit('client-request', requestLog);

    try {
        const response = await fetch(`${PYTHON_API}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        });

        const contentType = response.headers.get('content-type');
        res.set('Content-Type', contentType);

        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            res.json(data);
        } else {
            const buffer = await response.buffer();
            res.send(buffer);
        }
    } catch (err) {
        res.status(500).json({ error: 'Proxy error', message: err.message });
    }
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Proxy server + WebSocket running at http://localhost:${PORT}`);
});
