// RailGate Monitor - Railway Gate Management System JavaScript

// Global variables
let currentUser = null;
let trainData = [];
let gateStatus = 'CLOSED';
let updateInterval = null;

// Sample train data (in production, this would come from API)
const sampleTrainData = [
    {
        trainNumber: 'EXP-12345',
        arrivalTime: '14:30',
        gateClosure: '14:25',
        duration: '8 min',
        status: 'ontime'
    },
    {
        trainNumber: 'LOC-67890',
        arrivalTime: '14:45',
        gateClosure: '14:40',
        duration: '6 min',
        status: 'delayed'
    },
    {
        trainNumber: 'FRT-11111',
        arrivalTime: '15:15',
        gateClosure: '15:10',
        duration: '12 min',
        status: 'approaching'
    },
    {
        trainNumber: 'EXP-22222',
        arrivalTime: '15:45',
        gateClosure: '15:40',
        duration: '7 min',
        status: 'ontime'
    },
    {
        trainNumber: 'PSG-33333',
        arrivalTime: '16:20',
        gateClosure: '16:15',
        duration: '9 min',
        status: 'ontime'
    }
];

// Sample live updates
const sampleUpdates = [
    {
        icon: 'fa-info-circle',
        title: 'Gate Status Update',
        message: 'Gate #3 is currently closed for Train EXP-12345',
        time: '2 minutes ago'
    },
    {
        icon: 'fa-clock',
        title: 'Schedule Change',
        message: 'Train LOC-67890 delayed by 15 minutes due to technical issues',
        time: '5 minutes ago'
    },
    {
        icon: 'fa-route',
        title: 'Alternative Route',
        message: 'Bridge Road recommended as fastest alternative route',
        time: '8 minutes ago'
    },
    {
        icon: 'fa-exclamation-triangle',
        title: 'Traffic Advisory',
        message: 'Heavy traffic reported on Highway Bypass route',
        time: '12 minutes ago'
    }
];

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('railgate_user');
    const savedLocation = localStorage.getItem('railgate_location');
    
    if (savedUser && savedLocation) {
        currentUser = { name: savedUser, location: savedLocation };
        showDashboard();
    } else {
        showLoginScreen();
    }
    
    // Add event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const location = formData.get('location');
    
    if (!username || !location) {
        showNotification('Please fill in all fields.', 'error');
        return;
    }
    
    // Save user data
    currentUser = { name: username, location: location };
    localStorage.setItem('railgate_user', username);
    localStorage.setItem('railgate_location', location);
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Accessing System...';
    submitBtn.disabled = true;
    
    // Simulate login process
    setTimeout(() => {
        showNotification('Login successful! Welcome to Gate Alert.', 'success');
        showDashboard();
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }, 2000);
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('railgate_user');
        localStorage.removeItem('railgate_location');
        currentUser = null;
        
        // Stop updates
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
        
        showLoginScreen();
        showNotification('Logged out successfully.', 'success');
    }
}

function showLoginScreen() {
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('main-dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('main-dashboard').style.display = 'block';
    
    // Update user info
    updateUserInterface();
    
    // Load initial data
    loadTrainSchedule();
    loadLiveUpdates();
    updateGateStatus();
    
    // Start real-time updates
    startRealTimeUpdates();
    
    // Update footer timestamp
    updateLastUpdated();
}

function updateUserInterface() {
    if (currentUser) {
        document.getElementById('welcome-user').textContent = `Welcome, ${currentUser.name}`;
        document.getElementById('user-location').textContent = getLocationName(currentUser.location);
    }
}

function getLocationName(locationCode) {
    const locations = {
        'pune-junction': 'Pune Junction',
        'shivajinagar': 'Shivajinagar',
        'khadki': 'Khadki',
        'pimpri': 'Pimpri',
        'chinchwad': 'Chinchwad',
        'akurdi': 'Akurdi',
        'dehu-road': 'Dehu Road',
        'talegaon': 'Talegaon',
        'lonavala': 'Lonavala',
        'karjat': 'Karjat',
        'hadapsar': 'Hadapsar',
        'mundhwa': 'Mundhwa',
        'loni-kalbhor': 'Loni Kalbhor',
        'uruli-kanchan': 'Uruli Kanchan',
        'yerwada': 'Yerwada',
        'ghorpadi': 'Ghorpadi',
        'mundhwa-kharadi': 'Mundhwa-Kharadi',
        'wagholi': 'Wagholi',
        'manjari': 'Manjari',
        'bhigwan': 'Bhigwan',
        'daund': 'Daund',
        'indapur': 'Indapur',
        'jejuri': 'Jejuri',
        'saswad': 'Saswad',
        'dive-ghat': 'Dive Ghat',
        'katraj': 'Katraj',
        'warje': 'Warje',
        'kothrud': 'Kothrud',
        'bavdhan': 'Bavdhan',
        'pashan': 'Pashan',
        'hinjewadi': 'Hinjewadi',
        'wakad': 'Wakad',
        'baner': 'Baner',
        'aundh': 'Aundh',
        'sangamner': 'Sangamner',
        'ahmednagar': 'Ahmednagar',
        'shirur': 'Shirur',
        'chakan': 'Chakan',
        'rajgurunagar': 'Rajgurunagar',
        'manchar': 'Manchar',
        'alephata': 'Alephata',
        'junnar': 'Junnar',
        'ambegaon': 'Ambegaon',
        'ghodegaon': 'Ghodegaon',
        'khed': 'Khed',
        'chakan-bypass': 'Chakan Bypass',
        'bhosari': 'Bhosari',
        'nigdi': 'Nigdi',
        'dapodi': 'Dapodi',
        'kasarwadi': 'Kasarwadi',
        'phugewadi': 'Phugewadi'
    };
    return locations[locationCode] || 'Unknown Location';
}

function loadTrainSchedule() {
    const scheduleList = document.getElementById('train-schedule');
    if (!scheduleList) return;
    
    scheduleList.innerHTML = '';
    
    sampleTrainData.forEach(train => {
        const scheduleItem = document.createElement('div');
        scheduleItem.className = 'schedule-item';
        
        scheduleItem.innerHTML = `
            <div class="train-number">${train.trainNumber}</div>
            <div class="arrival-time">${train.arrivalTime}</div>
            <div class="gate-closure">${train.gateClosure}</div>
            <div class="duration">${train.duration}</div>
            <div class="train-status status-${train.status}">${getStatusText(train.status)}</div>
        `;
        
        scheduleList.appendChild(scheduleItem);
    });
}

function getStatusText(status) {
    const statusTexts = {
        'ontime': 'On Time',
        'delayed': 'Delayed',
        'approaching': 'Approaching'
    };
    return statusTexts[status] || 'Unknown';
}

function loadLiveUpdates() {
    const updateFeed = document.getElementById('update-feed');
    if (!updateFeed) return;
    
    updateFeed.innerHTML = '';
    
    sampleUpdates.forEach(update => {
        const updateItem = document.createElement('div');
        updateItem.className = 'update-item';
        
        updateItem.innerHTML = `
            <div class="update-icon">
                <i class="fas ${update.icon}"></i>
            </div>
            <div class="update-content">
                <h4>${update.title}</h4>
                <p>${update.message}</p>
                <div class="update-time">${update.time}</div>
            </div>
        `;
        
        updateFeed.appendChild(updateItem);
    });
}

function updateGateStatus() {
    const gateStatusElement = document.getElementById('gate-status');
    const gateStatusCard = document.querySelector('.gate-status');
    
    if (gateStatusElement && gateStatusCard) {
        // Simulate dynamic gate status
        const statuses = ['CLOSED', 'OPEN'];
        const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
        
        gateStatusElement.textContent = randomStatus;
        
        if (randomStatus === 'OPEN') {
            gateStatusCard.classList.add('open');
        } else {
            gateStatusCard.classList.remove('open');
        }
        
        gateStatus = randomStatus;
    }
    
    // Update other status values
    const trainCount = document.getElementById('train-count');
    const waitTime = document.getElementById('wait-time');
    
    if (trainCount) {
        const remainingTrains = Math.floor(Math.random() * 8) + 3;
        trainCount.textContent = remainingTrains;
    }
    
    if (waitTime) {
        const avgWait = Math.floor(Math.random() * 15) + 5;
        waitTime.textContent = `${avgWait} min`;
    }
}

function startRealTimeUpdates() {
    // Update every 30 seconds
    updateInterval = setInterval(() => {
        updateGateStatus();
        updateLastUpdated();
        
        // Occasionally add new updates
        if (Math.random() < 0.3) {
            addRandomUpdate();
        }
    }, 30000);
}

function addRandomUpdate() {
    const randomUpdates = [
        {
            icon: 'fa-info-circle',
            title: 'System Update',
            message: 'Real-time data refreshed successfully',
            time: 'Just now'
        },
        {
            icon: 'fa-train',
            title: 'Train Passed',
            message: 'Express train cleared the crossing safely',
            time: 'Just now'
        }
    ];
    
    const updateFeed = document.getElementById('update-feed');
    if (updateFeed) {
        const randomUpdate = randomUpdates[Math.floor(Math.random() * randomUpdates.length)];
        
        const updateItem = document.createElement('div');
        updateItem.className = 'update-item';
        updateItem.style.opacity = '0';
        updateItem.style.transform = 'translateY(-20px)';
        
        updateItem.innerHTML = `
            <div class="update-icon">
                <i class="fas ${randomUpdate.icon}"></i>
            </div>
            <div class="update-content">
                <h4>${randomUpdate.title}</h4>
                <p>${randomUpdate.message}</p>
                <div class="update-time">${randomUpdate.time}</div>
            </div>
        `;
        
        updateFeed.insertBefore(updateItem, updateFeed.firstChild);
        
        // Animate in
        setTimeout(() => {
            updateItem.style.transition = 'all 0.3s ease';
            updateItem.style.opacity = '1';
            updateItem.style.transform = 'translateY(0)';
        }, 100);
        
        // Remove old updates if too many
        const updates = updateFeed.querySelectorAll('.update-item');
        if (updates.length > 8) {
            updateFeed.removeChild(updates[updates.length - 1]);
        }
    }
}

function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });
        lastUpdatedElement.textContent = timeString;
    }
}

// Utility function for notifications
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    // Set background color based on type
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
    }
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Additional interactive features
document.addEventListener('click', function(e) {
    // Route card interactions
    if (e.target.closest('.route-card')) {
        const routeCard = e.target.closest('.route-card');
        const routeName = routeCard.querySelector('h3').textContent;
        showNotification(`Route information for ${routeName} has been noted.`, 'info');
    }
    
    // Status card interactions
    if (e.target.closest('.status-card')) {
        const statusCard = e.target.closest('.status-card');
        const statusType = statusCard.querySelector('h3').textContent;
        showNotification(`${statusType} details viewed.`, 'info');
    }
});

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, reduce update frequency
        if (updateInterval) {
            clearInterval(updateInterval);
        }
    } else {
        // Page is visible, resume normal updates
        if (currentUser && document.getElementById('main-dashboard').style.display !== 'none') {
            startRealTimeUpdates();
            updateGateStatus();
            updateLastUpdated();
        }
    }
});

// Initialize timestamp on page load
document.addEventListener('DOMContentLoaded', function() {
    updateLastUpdated();
});