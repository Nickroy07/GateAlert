// Gate Alert - Node.js Backend Server

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

// Load environment variables
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
            scriptSrc: ["'self'"],
            fontSrc: ["'self'", "https://cdnjs.cloudflare.com"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
}));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

// Sample data storage
let trainData = [
    {
        id: '1',
        trainNumber: 'EXP-12345',
        arrivalTime: '14:30',
        gateClosure: '14:25',
        duration: '8 min',
        status: 'ontime',
        route: 'Mumbai-Delhi',
        platform: '3'
    },
    {
        id: '2',
        trainNumber: 'LOC-67890',
        arrivalTime: '14:45',
        gateClosure: '14:40',
        duration: '6 min',
        status: 'delayed',
        route: 'Local Service',
        platform: '1'
    },
    {
        id: '3',
        trainNumber: 'FRT-11111',
        arrivalTime: '15:15',
        gateClosure: '15:10',
        duration: '12 min',
        status: 'approaching',
        route: 'Freight Service',
        platform: '2'
    }
];

let gateStatus = {
    id: 'gate-001',
    status: 'CLOSED',
    lastUpdated: new Date(),
    nextOpening: '14:45',
    location: 'Central Railway Station'
};

// API Routes
app.get('/api/trains', (req, res) => {
    res.json({
        success: true,
        data: trainData,
        timestamp: new Date().toISOString()
    });
});

app.get('/api/gate/status', (req, res) => {
    res.json({
        success: true,
        data: gateStatus,
        timestamp: new Date().toISOString()
    });
});

app.get('/api/stats', (req, res) => {
    const stats = {
        totalTrains: trainData.length,
        onTimeTrains: trainData.filter(t => t.status === 'ontime').length,
        delayedTrains: trainData.filter(t => t.status === 'delayed').length,
        gateStatus: gateStatus.status,
        averageWaitTime: `${Math.floor(Math.random() * 15) + 5} min`,
        trainsToday: Math.floor(Math.random() * 30) + 20
    };
    
    res.json({
        success: true,
        data: stats,
        timestamp: new Date().toISOString()
    });
});

app.post('/api/auth/login', (req, res) => {
    const { username, location } = req.body;
    
    if (!username || !location) {
        return res.status(400).json({
            success: false,
            error: 'Username and location are required'
        });
    }
    
    res.json({
        success: true,
        data: {
            user: { username, location },
            sessionToken: uuidv4()
        }
    });
});

// Serve the main application
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
const server = app.listen(PORT, () => {
    console.log(`🚂 Gate Alert Server running on port ${PORT}`);
    console.log(`📍 Access the application at: http://localhost:${PORT}`);
});

// WebSocket setup
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('📡 New WebSocket connection established');
    
    ws.send(JSON.stringify({
        type: 'initial_data',
        data: { trains: trainData, gateStatus }
    }));
    
    ws.on('close', () => {
        console.log('📡 WebSocket connection closed');
    });
});

// Simulate real-time updates
setInterval(() => {
    if (Math.random() < 0.3) {
        const randomTrain = trainData[Math.floor(Math.random() * trainData.length)];
        const statuses = ['ontime', 'delayed', 'approaching'];
        randomTrain.status = statuses[Math.floor(Math.random() * statuses.length)];
        
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({
                    type: 'train_update',
                    data: randomTrain
                }));
            }
        });
    }
}, 30000);
