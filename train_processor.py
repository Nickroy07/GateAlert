#!/usr/bin/env python3
\"\"\"
RailGate Monitor - Python Data Processing Module

This module handles:
- Train schedule data processing
- Route optimization calculations
- Traffic pattern analysis
- Real-time data synchronization with Node.js backend

Author: RailGate Development Team
Version: 1.0.0
\"\"\"

import json
import datetime
import time
import requests
import random
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('railgate_processor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class TrainSchedule:
    \"\"\"Data class for train schedule information\"\"\"
    train_number: str
    arrival_time: str
    departure_time: str
    platform: str
    route: str
    status: str
    delay_minutes: int = 0
    gate_closure_duration: int = 8
    priority: str = 'normal'

@dataclass
class GateStatus:
    \"\"\"Data class for gate status information\"\"\"
    gate_id: str
    status: str  # OPEN, CLOSED, MAINTENANCE
    last_updated: datetime.datetime
    next_scheduled_closure: Optional[str] = None
    operator_id: Optional[str] = None
    maintenance_reason: Optional[str] = None

@dataclass
class Route:
    \"\"\"Data class for alternative route information\"\"\"
    route_id: str
    name: str
    distance_km: float
    additional_time_minutes: int
    traffic_level: str  # low, medium, high
    road_conditions: str
    recommended: bool = False
    toll_cost: float = 0.0

class TrainDataProcessor:
    \"\"\"Main class for processing train and gate data\"\"\"
    
    def __init__(self, api_base_url: str = \"http://localhost:3000/api\"):
        self.api_base_url = api_base_url
        self.train_schedules: List[TrainSchedule] = []
        self.gate_status: Optional[GateStatus] = None
        self.alternative_routes: List[Route] = []
        self.is_running = False
        
        # Sample train data for simulation
        self.sample_trains = [
            TrainSchedule(
                train_number=\"EXP-12345\",
                arrival_time=\"14:30\",
                departure_time=\"14:38\",
                platform=\"3\",
                route=\"Mumbai-Delhi Express\",
                status=\"ontime\",
                priority=\"high\"
            ),
            TrainSchedule(
                train_number=\"LOC-67890\",
                arrival_time=\"14:45\",
                departure_time=\"14:51\",
                platform=\"1\",
                route=\"Local Passenger Service\",
                status=\"delayed\",
                delay_minutes=15
            ),
            TrainSchedule(
                train_number=\"FRT-11111\",
                arrival_time=\"15:15\",
                departure_time=\"15:27\",
                platform=\"2\",
                route=\"Freight Service\",
                status=\"approaching\",
                gate_closure_duration=12,
                priority=\"low\"
            ),
            TrainSchedule(
                train_number=\"EXP-22222\",
                arrival_time=\"15:45\",
                departure_time=\"15:52\",
                platform=\"4\",
                route=\"Chennai-Kolkata Express\",
                status=\"ontime\",
                priority=\"high\"
            ),
            TrainSchedule(
                train_number=\"PSG-33333\",
                arrival_time=\"16:20\",
                departure_time=\"16:29\",
                platform=\"1\",
                route=\"Inter-city Passenger\",
                status=\"ontime\"
            )
        ]
        
        # Initialize alternative routes
        self.initialize_routes()
    
    def initialize_routes(self):
        \"\"\"Initialize alternative route data\"\"\"
        self.alternative_routes = [
            Route(
                route_id=\"R001\",
                name=\"Highway Bypass\",
                distance_km=8.2,
                additional_time_minutes=15,
                traffic_level=\"medium\",
                road_conditions=\"good\",
                toll_cost=25.0
            ),
            Route(
                route_id=\"R002\",
                name=\"City Center Route\",
                distance_km=7.8,
                additional_time_minutes=12,
                traffic_level=\"high\",
                road_conditions=\"fair\",
                toll_cost=0.0
            ),
            Route(
                route_id=\"R003\",
                name=\"Industrial Zone\",
                distance_km=9.1,
                additional_time_minutes=18,
                traffic_level=\"low\",
                road_conditions=\"excellent\",
                toll_cost=15.0
            ),
            Route(
                route_id=\"R004\",
                name=\"Bridge Road\",
                distance_km=6.5,
                additional_time_minutes=8,
                traffic_level=\"low\",
                road_conditions=\"good\",
                recommended=True,
                toll_cost=10.0
            )
        ]
    
    def calculate_gate_closure_schedule(self) -> List[Dict]:
        \"\"\"Calculate when gates should be closed based on train schedule\"\"\"
        closure_schedule = []
        
        for train in self.sample_trains:
            # Parse arrival time
            arrival_hour, arrival_minute = map(int, train.arrival_time.split(':'))
            arrival_datetime = datetime.datetime.now().replace(
                hour=arrival_hour, 
                minute=arrival_minute, 
                second=0, 
                microsecond=0
            )
            
            # Calculate closure start time (5 minutes before arrival)
            closure_start = arrival_datetime - datetime.timedelta(minutes=5)
            
            # Calculate closure end time (based on train type and duration)
            closure_end = arrival_datetime + datetime.timedelta(minutes=train.gate_closure_duration)
            
            closure_schedule.append({
                'train_number': train.train_number,
                'closure_start': closure_start.strftime('%H:%M'),
                'closure_end': closure_end.strftime('%H:%M'),
                'duration_minutes': train.gate_closure_duration + 5,
                'priority': train.priority,
                'platform': train.platform
            })
        
        # Sort by closure start time
        closure_schedule.sort(key=lambda x: x['closure_start'])
        
        logger.info(f\"Generated gate closure schedule for {len(closure_schedule)} trains\")
        return closure_schedule
    
    def optimize_routes(self, current_traffic_data: Dict = None) -> List[Route]:
        \"\"\"Optimize alternative routes based on current conditions\"\"\"
        optimized_routes = self.alternative_routes.copy()
        
        # Simulate real-time traffic analysis
        for route in optimized_routes:
            # Add random traffic variations
            traffic_multiplier = {
                'low': random.uniform(0.8, 1.1),
                'medium': random.uniform(1.0, 1.3),
                'high': random.uniform(1.2, 1.8)
            }.get(route.traffic_level, 1.0)
            
            # Adjust time based on traffic
            route.additional_time_minutes = int(route.additional_time_minutes * traffic_multiplier)
            
            # Update traffic level based on time of day
            current_hour = datetime.datetime.now().hour
            if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # Rush hours
                if route.traffic_level == 'low':
                    route.traffic_level = 'medium'
                elif route.traffic_level == 'medium':
                    route.traffic_level = 'high'
        
        # Re-evaluate recommendations
        optimized_routes.sort(key=lambda r: r.additional_time_minutes)
        
        # Mark the fastest route as recommended
        for route in optimized_routes:
            route.recommended = False
        
        if optimized_routes:
            optimized_routes[0].recommended = True
        
        logger.info(f\"Optimized {len(optimized_routes)} alternative routes\")
        return optimized_routes
    
    def predict_wait_times(self) -> Dict[str, int]:
        \"\"\"Predict wait times based on train schedule and historical data\"\"\"
        current_time = datetime.datetime.now()
        wait_predictions = {}
        
        closure_schedule = self.calculate_gate_closure_schedule()
        
        for closure in closure_schedule:
            closure_start_time = datetime.datetime.strptime(closure['closure_start'], '%H:%M')
            closure_start_time = current_time.replace(
                hour=closure_start_time.hour,
                minute=closure_start_time.minute,
                second=0,
                microsecond=0
            )
            
            # If closure is in the future, calculate wait time
            if closure_start_time > current_time:
                minutes_until_closure = int((closure_start_time - current_time).total_seconds() / 60)
                wait_predictions[closure['train_number']] = {
                    'minutes_until_closure': minutes_until_closure,
                    'closure_duration': closure['duration_minutes'],
                    'total_wait_if_caught': closure['duration_minutes'],
                    'recommended_action': self._get_wait_recommendation(minutes_until_closure, closure['duration_minutes'])
                }
        
        logger.info(f\"Generated wait time predictions for {len(wait_predictions)} upcoming closures\")
        return wait_predictions
    
    def _get_wait_recommendation(self, minutes_until: int, duration: int) -> str:
        \"\"\"Get recommendation based on wait time analysis\"\"\"
        if minutes_until <= 2:
            return \"STOP - Gate closing very soon\"
        elif minutes_until <= 5:
            return \"CAUTION - Consider alternative route\"
        elif duration > 10:
            return \"PLAN - Long closure expected, use alternative route\"
        else:
            return \"PROCEED - Sufficient time to cross\"
    
    def analyze_traffic_patterns(self) -> Dict:
        \"\"\"Analyze traffic patterns and generate insights\"\"\"
        current_hour = datetime.datetime.now().hour
        current_day = datetime.datetime.now().strftime('%A')
        
        # Simulate traffic analysis
        analysis = {
            'current_conditions': {
                'time': datetime.datetime.now().strftime('%H:%M'),
                'day': current_day,
                'traffic_intensity': self._get_traffic_intensity(current_hour),
                'weather_impact': random.choice(['none', 'light', 'moderate', 'heavy']),
                'special_events': random.choice([None, 'School hours', 'Market day', 'Festival'])
            },
            'predictions': {
                'next_hour_traffic': self._get_traffic_intensity(current_hour + 1),
                'peak_hours_today': ['08:00-09:30', '17:30-19:00'],
                'recommended_travel_window': self._get_recommended_window(current_hour)
            },
            'statistics': {
                'average_daily_closures': random.randint(20, 35),
                'longest_closure_today': f\"{random.randint(8, 15)} minutes\",
                'busiest_platform': random.choice(['1', '2', '3', '4']),
                'on_time_percentage': random.randint(75, 95)
            }
        }
        
        logger.info(\"Generated traffic pattern analysis\")
        return analysis
    
    def _get_traffic_intensity(self, hour: int) -> str:
        \"\"\"Get traffic intensity for a given hour\"\"\"
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 'high'
        elif 10 <= hour <= 16 or 19 <= hour <= 21:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommended_window(self, current_hour: int) -> str:
        \"\"\"Get recommended travel window\"\"\"
        if current_hour < 7:
            return \"07:00-07:30 (Before morning rush)\"
        elif 7 <= current_hour <= 9:
            return \"10:00-11:00 (After morning rush)\"
        elif 9 < current_hour < 17:
            return \"Now - Good time to travel\"
        elif 17 <= current_hour <= 19:
            return \"20:00-21:00 (After evening rush)\"
        else:
            return \"Now - Light traffic period\"
    
    def sync_with_backend(self):
        \"\"\"Synchronize processed data with Node.js backend\"\"\"
        try:
            # Prepare data for sync
            processed_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'gate_closure_schedule': self.calculate_gate_closure_schedule(),
                'optimized_routes': [
                    {
                        'id': route.route_id,
                        'name': route.name,
                        'distance': f\"+{route.distance_km} km\",
                        'additional_time': f\"{route.additional_time_minutes} min longer\",
                        'traffic_level': route.traffic_level,
                        'recommended': route.recommended,
                        'toll_cost': route.toll_cost
                    } for route in self.optimize_routes()
                ],
                'wait_predictions': self.predict_wait_times(),
                'traffic_analysis': self.analyze_traffic_patterns()
            }
            
            # In a real implementation, this would send data to the backend
            # For now, we'll save it to a file that the backend can read
            with open('processed_data.json', 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
            logger.info(\"Successfully synchronized data with backend\")
            return True
            
        except Exception as e:
            logger.error(f\"Failed to sync with backend: {e}\")
            return False
    
    def generate_alerts(self) -> List[Dict]:
        \"\"\"Generate alerts based on current conditions\"\"\"
        alerts = []
        current_time = datetime.datetime.now()
        
        # Check for delayed trains
        for train in self.sample_trains:
            if train.status == 'delayed' and train.delay_minutes > 10:
                alerts.append({
                    'type': 'delay_alert',
                    'priority': 'high',
                    'message': f\"Train {train.train_number} delayed by {train.delay_minutes} minutes\",
                    'timestamp': current_time.isoformat(),
                    'train_number': train.train_number
                })
        
        # Check for upcoming long closures
        closure_schedule = self.calculate_gate_closure_schedule()
        for closure in closure_schedule:
            if closure['duration_minutes'] > 10:
                alerts.append({
                    'type': 'long_closure_alert',
                    'priority': 'medium',
                    'message': f\"Extended gate closure expected: {closure['duration_minutes']} minutes for {closure['train_number']}\",
                    'timestamp': current_time.isoformat(),
                    'closure_start': closure['closure_start']
                })
        
        # Check traffic conditions
        traffic_analysis = self.analyze_traffic_patterns()
        if traffic_analysis['current_conditions']['traffic_intensity'] == 'high':
            alerts.append({
                'type': 'traffic_alert',
                'priority': 'medium',
                'message': \"High traffic intensity detected. Consider alternative routes.\",
                'timestamp': current_time.isoformat()
            })
        
        logger.info(f\"Generated {len(alerts)} alerts\")
        return alerts
    
    def start_processing(self, interval_seconds: int = 30):
        \"\"\"Start the data processing loop\"\"\"
        self.is_running = True
        logger.info(f\"Starting data processing with {interval_seconds}s interval\")
        
        while self.is_running:
            try:
                # Process data
                self.sync_with_backend()
                
                # Generate and log alerts
                alerts = self.generate_alerts()
                for alert in alerts:
                    logger.warning(f\"ALERT: {alert['message']}\")
                
                # Wait for next iteration
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info(\"Received interrupt signal, stopping...\")
                self.stop_processing()
            except Exception as e:
                logger.error(f\"Error in processing loop: {e}\")
                time.sleep(5)  # Short delay before retrying
    
    def stop_processing(self):
        \"\"\"Stop the data processing loop\"\"\"
        self.is_running = False
        logger.info(\"Data processing stopped\")

def main():
    \"\"\"Main function to run the data processor\"\"\"
    processor = TrainDataProcessor()
    
    # Run one-time analysis
    logger.info(\"Running initial data analysis...\")
    
    closure_schedule = processor.calculate_gate_closure_schedule()
    print(\"\n=== Gate Closure Schedule ===\")
    for closure in closure_schedule:
        print(f\"{closure['train_number']}: {closure['closure_start']} - {closure['closure_end']} ({closure['duration_minutes']} min)\")
    
    optimized_routes = processor.optimize_routes()
    print(\"\n=== Optimized Alternative Routes ===\")
    for route in optimized_routes:
        status = \"[RECOMMENDED]\" if route.recommended else \"\"
        print(f\"{route.name}: +{route.additional_time_minutes} min, Traffic: {route.traffic_level} {status}\")
    
    wait_predictions = processor.predict_wait_times()
    print(\"\n=== Wait Time Predictions ===\")
    for train, prediction in wait_predictions.items():
        print(f\"{train}: {prediction['minutes_until_closure']} min until closure, {prediction['recommended_action']}\")
    
    traffic_analysis = processor.analyze_traffic_patterns()
    print(\"\n=== Traffic Analysis ===\")
    print(f\"Current traffic: {traffic_analysis['current_conditions']['traffic_intensity']}\")
    print(f\"Recommended window: {traffic_analysis['predictions']['recommended_travel_window']}\")
    
    alerts = processor.generate_alerts()
    print(\"\n=== Active Alerts ===\")
    for alert in alerts:
        print(f\"[{alert['priority'].upper()}] {alert['message']}\")
    
    # Sync with backend
    processor.sync_with_backend()
    print(\"\n✅ Data synchronized with backend (saved to processed_data.json)\")
    
    # Ask if user wants to start continuous processing
    start_continuous = input(\"\nStart continuous processing? (y/n): \").lower().strip()
    if start_continuous == 'y':
        print(\"Starting continuous processing... Press Ctrl+C to stop.\")
        processor.start_processing()

if __name__ == \"__main__\":
    main()"#!/usr/bin/env python3
\"\"\"
RailGate Monitor - Python Data Processing Module

This module handles:
- Train schedule data processing
- Route optimization calculations
- Traffic pattern analysis
- Real-time data synchronization with Node.js backend

Author: RailGate Development Team
Version: 1.0.0
\"\"\"

import json
import datetime
import time
import requests
import random
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('railgate_processor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class TrainSchedule:
    \"\"\"Data class for train schedule information\"\"\"
    train_number: str
    arrival_time: str
    departure_time: str
    platform: str
    route: str
    status: str
    delay_minutes: int = 0
    gate_closure_duration: int = 8
    priority: str = 'normal'

@dataclass
class GateStatus:
    \"\"\"Data class for gate status information\"\"\"
    gate_id: str
    status: str  # OPEN, CLOSED, MAINTENANCE
    last_updated: datetime.datetime
    next_scheduled_closure: Optional[str] = None
    operator_id: Optional[str] = None
    maintenance_reason: Optional[str] = None

@dataclass
class Route:
    \"\"\"Data class for alternative route information\"\"\"
    route_id: str
    name: str
    distance_km: float
    additional_time_minutes: int
    traffic_level: str  # low, medium, high
    road_conditions: str
    recommended: bool = False
    toll_cost: float = 0.0

class TrainDataProcessor:
    \"\"\"Main class for processing train and gate data\"\"\"
    
    def __init__(self, api_base_url: str = \"http://localhost:3000/api\"):
        self.api_base_url = api_base_url
        self.train_schedules: List[TrainSchedule] = []
        self.gate_status: Optional[GateStatus] = None
        self.alternative_routes: List[Route] = []
        self.is_running = False
        
        # Sample train data for simulation
        self.sample_trains = [
            TrainSchedule(
                train_number=\"EXP-12345\",
                arrival_time=\"14:30\",
                departure_time=\"14:38\",
                platform=\"3\",
                route=\"Mumbai-Delhi Express\",
                status=\"ontime\",
                priority=\"high\"
            ),
            TrainSchedule(
                train_number=\"LOC-67890\",
                arrival_time=\"14:45\",
                departure_time=\"14:51\",
                platform=\"1\",
                route=\"Local Passenger Service\",
                status=\"delayed\",
                delay_minutes=15
            ),
            TrainSchedule(
                train_number=\"FRT-11111\",
                arrival_time=\"15:15\",
                departure_time=\"15:27\",
                platform=\"2\",
                route=\"Freight Service\",
                status=\"approaching\",
                gate_closure_duration=12,
                priority=\"low\"
            ),
            TrainSchedule(
                train_number=\"EXP-22222\",
                arrival_time=\"15:45\",
                departure_time=\"15:52\",
                platform=\"4\",
                route=\"Chennai-Kolkata Express\",
                status=\"ontime\",
                priority=\"high\"
            ),
            TrainSchedule(
                train_number=\"PSG-33333\",
                arrival_time=\"16:20\",
                departure_time=\"16:29\",
                platform=\"1\",
                route=\"Inter-city Passenger\",
                status=\"ontime\"
            )
        ]
        
        # Initialize alternative routes
        self.initialize_routes()
    
    def initialize_routes(self):
        \"\"\"Initialize alternative route data\"\"\"
        self.alternative_routes = [
            Route(
                route_id=\"R001\",
                name=\"Highway Bypass\",
                distance_km=8.2,
                additional_time_minutes=15,
                traffic_level=\"medium\",
                road_conditions=\"good\",
                toll_cost=25.0
            ),
            Route(
                route_id=\"R002\",
                name=\"City Center Route\",
                distance_km=7.8,
                additional_time_minutes=12,
                traffic_level=\"high\",
                road_conditions=\"fair\",
                toll_cost=0.0
            ),
            Route(
                route_id=\"R003\",
                name=\"Industrial Zone\",
                distance_km=9.1,
                additional_time_minutes=18,
                traffic_level=\"low\",
                road_conditions=\"excellent\",
                toll_cost=15.0
            ),
            Route(
                route_id=\"R004\",
                name=\"Bridge Road\",
                distance_km=6.5,
                additional_time_minutes=8,
                traffic_level=\"low\",
                road_conditions=\"good\",
                recommended=True,
                toll_cost=10.0
            )
        ]
    
    def calculate_gate_closure_schedule(self) -> List[Dict]:
        \"\"\"Calculate when gates should be closed based on train schedule\"\"\"
        closure_schedule = []
        
        for train in self.sample_trains:
            # Parse arrival time
            arrival_hour, arrival_minute = map(int, train.arrival_time.split(':'))
            arrival_datetime = datetime.datetime.now().replace(
                hour=arrival_hour, 
                minute=arrival_minute, 
                second=0, 
                microsecond=0
            )
            
            # Calculate closure start time (5 minutes before arrival)
            closure_start = arrival_datetime - datetime.timedelta(minutes=5)
            
            # Calculate closure end time (based on train type and duration)
            closure_end = arrival_datetime + datetime.timedelta(minutes=train.gate_closure_duration)
            
            closure_schedule.append({
                'train_number': train.train_number,
                'closure_start': closure_start.strftime('%H:%M'),
                'closure_end': closure_end.strftime('%H:%M'),
                'duration_minutes': train.gate_closure_duration + 5,
                'priority': train.priority,
                'platform': train.platform
            })
        
        # Sort by closure start time
        closure_schedule.sort(key=lambda x: x['closure_start'])
        
        logger.info(f\"Generated gate closure schedule for {len(closure_schedule)} trains\")
        return closure_schedule
    
    def optimize_routes(self, current_traffic_data: Dict = None) -> List[Route]:
        \"\"\"Optimize alternative routes based on current conditions\"\"\"
        optimized_routes = self.alternative_routes.copy()
        
        # Simulate real-time traffic analysis
        for route in optimized_routes:
            # Add random traffic variations
            traffic_multiplier = {
                'low': random.uniform(0.8, 1.1),
                'medium': random.uniform(1.0, 1.3),
                'high': random.uniform(1.2, 1.8)
            }.get(route.traffic_level, 1.0)
            
            # Adjust time based on traffic
            route.additional_time_minutes = int(route.additional_time_minutes * traffic_multiplier)
            
            # Update traffic level based on time of day
            current_hour = datetime.datetime.now().hour
            if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # Rush hours
                if route.traffic_level == 'low':
                    route.traffic_level = 'medium'
                elif route.traffic_level == 'medium':
                    route.traffic_level = 'high'
        
        # Re-evaluate recommendations
        optimized_routes.sort(key=lambda r: r.additional_time_minutes)
        
        # Mark the fastest route as recommended
        for route in optimized_routes:
            route.recommended = False
        
        if optimized_routes:
            optimized_routes[0].recommended = True
        
        logger.info(f\"Optimized {len(optimized_routes)} alternative routes\")
        return optimized_routes
    
    def predict_wait_times(self) -> Dict[str, int]:
        \"\"\"Predict wait times based on train schedule and historical data\"\"\"
        current_time = datetime.datetime.now()
        wait_predictions = {}
        
        closure_schedule = self.calculate_gate_closure_schedule()
        
        for closure in closure_schedule:
            closure_start_time = datetime.datetime.strptime(closure['closure_start'], '%H:%M')
            closure_start_time = current_time.replace(
                hour=closure_start_time.hour,
                minute=closure_start_time.minute,
                second=0,
                microsecond=0
            )
            
            # If closure is in the future, calculate wait time
            if closure_start_time > current_time:
                minutes_until_closure = int((closure_start_time - current_time).total_seconds() / 60)
                wait_predictions[closure['train_number']] = {
                    'minutes_until_closure': minutes_until_closure,
                    'closure_duration': closure['duration_minutes'],
                    'total_wait_if_caught': closure['duration_minutes'],
                    'recommended_action': self._get_wait_recommendation(minutes_until_closure, closure['duration_minutes'])
                }
        
        logger.info(f\"Generated wait time predictions for {len(wait_predictions)} upcoming closures\")
        return wait_predictions
    
    def _get_wait_recommendation(self, minutes_until: int, duration: int) -> str:
        \"\"\"Get recommendation based on wait time analysis\"\"\"
        if minutes_until <= 2:
            return \"STOP - Gate closing very soon\"
        elif minutes_until <= 5:
            return \"CAUTION - Consider alternative route\"
        elif duration > 10:
            return \"PLAN - Long closure expected, use alternative route\"
        else:
            return \"PROCEED - Sufficient time to cross\"
    
    def analyze_traffic_patterns(self) -> Dict:
        \"\"\"Analyze traffic patterns and generate insights\"\"\"
        current_hour = datetime.datetime.now().hour
        current_day = datetime.datetime.now().strftime('%A')
        
        # Simulate traffic analysis
        analysis = {
            'current_conditions': {
                'time': datetime.datetime.now().strftime('%H:%M'),
                'day': current_day,
                'traffic_intensity': self._get_traffic_intensity(current_hour),
                'weather_impact': random.choice(['none', 'light', 'moderate', 'heavy']),
                'special_events': random.choice([None, 'School hours', 'Market day', 'Festival'])
            },
            'predictions': {
                'next_hour_traffic': self._get_traffic_intensity(current_hour + 1),
                'peak_hours_today': ['08:00-09:30', '17:30-19:00'],
                'recommended_travel_window': self._get_recommended_window(current_hour)
            },
            'statistics': {
                'average_daily_closures': random.randint(20, 35),
                'longest_closure_today': f\"{random.randint(8, 15)} minutes\",
                'busiest_platform': random.choice(['1', '2', '3', '4']),
                'on_time_percentage': random.randint(75, 95)
            }
        }
        
        logger.info(\"Generated traffic pattern analysis\")
        return analysis
    
    def _get_traffic_intensity(self, hour: int) -> str:
        \"\"\"Get traffic intensity for a given hour\"\"\"
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 'high'
        elif 10 <= hour <= 16 or 19 <= hour <= 21:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommended_window(self, current_hour: int) -> str:
        \"\"\"Get recommended travel window\"\"\"
        if current_hour < 7:
            return \"07:00-07:30 (Before morning rush)\"
        elif 7 <= current_hour <= 9:
            return \"10:00-11:00 (After morning rush)\"
        elif 9 < current_hour < 17:
            return \"Now - Good time to travel\"
        elif 17 <= current_hour <= 19:
            return \"20:00-21:00 (After evening rush)\"
        else:
            return \"Now - Light traffic period\"
    
    def sync_with_backend(self):
        \"\"\"Synchronize processed data with Node.js backend\"\"\"
        try:
            # Prepare data for sync
            processed_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'gate_closure_schedule': self.calculate_gate_closure_schedule(),
                'optimized_routes': [
                    {
                        'id': route.route_id,
                        'name': route.name,
                        'distance': f\"+{route.distance_km} km\",
                        'additional_time': f\"{route.additional_time_minutes} min longer\",
                        'traffic_level': route.traffic_level,
                        'recommended': route.recommended,
                        'toll_cost': route.toll_cost
                    } for route in self.optimize_routes()
                ],
                'wait_predictions': self.predict_wait_times(),
                'traffic_analysis': self.analyze_traffic_patterns()
            }
            
            # In a real implementation, this would send data to the backend
            # For now, we'll save it to a file that the backend can read
            with open('processed_data.json', 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
            logger.info(\"Successfully synchronized data with backend\")
            return True
            
        except Exception as e:
            logger.error(f\"Failed to sync with backend: {e}\")
            return False
    
    def generate_alerts(self) -> List[Dict]:
        \"\"\"Generate alerts based on current conditions\"\"\"
        alerts = []
        current_time = datetime.datetime.now()
        
        # Check for delayed trains
        for train in self.sample_trains:
            if train.status == 'delayed' and train.delay_minutes > 10:
                alerts.append({
                    'type': 'delay_alert',
                    'priority': 'high',
                    'message': f\"Train {train.train_number} delayed by {train.delay_minutes} minutes\",
                    'timestamp': current_time.isoformat(),
                    'train_number': train.train_number
                })
        
        # Check for upcoming long closures
        closure_schedule = self.calculate_gate_closure_schedule()
        for closure in closure_schedule:
            if closure['duration_minutes'] > 10:
                alerts.append({
                    'type': 'long_closure_alert',
                    'priority': 'medium',
                    'message': f\"Extended gate closure expected: {closure['duration_minutes']} minutes for {closure['train_number']}\",
                    'timestamp': current_time.isoformat(),
                    'closure_start': closure['closure_start']
                })
        
        # Check traffic conditions
        traffic_analysis = self.analyze_traffic_patterns()
        if traffic_analysis['current_conditions']['traffic_intensity'] == 'high':
            alerts.append({
                'type': 'traffic_alert',
                'priority': 'medium',
                'message': \"High traffic intensity detected. Consider alternative routes.\",
                'timestamp': current_time.isoformat()
            })
        
        logger.info(f\"Generated {len(alerts)} alerts\")
        return alerts
    
    def start_processing(self, interval_seconds: int = 30):
        \"\"\"Start the data processing loop\"\"\"
        self.is_running = True
        logger.info(f\"Starting data processing with {interval_seconds}s interval\")
        
        while self.is_running:
            try:
                # Process data
                self.sync_with_backend()
                
                # Generate and log alerts
                alerts = self.generate_alerts()
                for alert in alerts:
                    logger.warning(f\"ALERT: {alert['message']}\")
                
                # Wait for next iteration
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info(\"Received interrupt signal, stopping...\")
                self.stop_processing()
            except Exception as e:
                logger.error(f\"Error in processing loop: {e}\")
                time.sleep(5)  # Short delay before retrying
    
    def stop_processing(self):
        \"\"\"Stop the data processing loop\"\"\"
        self.is_running = False
        logger.info(\"Data processing stopped\")

def main():
    \"\"\"Main function to run the data processor\"\"\"
    processor = TrainDataProcessor()
    
    # Run one-time analysis
    logger.info(\"Running initial data analysis...\")
    
    closure_schedule = processor.calculate_gate_closure_schedule()
    print(\"\n=== Gate Closure Schedule ===\")
    for closure in closure_schedule:
        print(f\"{closure['train_number']}: {closure['closure_start']} - {closure['closure_end']} ({closure['duration_minutes']} min)\")
    
    optimized_routes = processor.optimize_routes()
    print(\"\n=== Optimized Alternative Routes ===\")
    for route in optimized_routes:
        status = \"[RECOMMENDED]\" if route.recommended else \"\"
        print(f\"{route.name}: +{route.additional_time_minutes} min, Traffic: {route.traffic_level} {status}\")
    
    wait_predictions = processor.predict_wait_times()
    print(\"\n=== Wait Time Predictions ===\")
    for train, prediction in wait_predictions.items():
        print(f\"{train}: {prediction['minutes_until_closure']} min until closure, {prediction['recommended_action']}\")
    
    traffic_analysis = processor.analyze_traffic_patterns()
    print(\"\n=== Traffic Analysis ===\")
    print(f\"Current traffic: {traffic_analysis['current_conditions']['traffic_intensity']}\")
    print(f\"Recommended window: {traffic_analysis['predictions']['recommended_travel_window']}\")
    
    alerts = processor.generate_alerts()
    print(\"\n=== Active Alerts ===\")
    for alert in alerts:
        print(f\"[{alert['priority'].upper()}] {alert['message']}\")
    
    # Sync with backend
    processor.sync_with_backend()
    print(\"\n✅ Data synchronized with backend (saved to processed_data.json)\")
    
    # Ask if user wants to start continuous processing
    start_continuous = input(\"\nStart continuous processing? (y/n): \").lower().strip()
    if start_continuous == 'y':
        print(\"Starting continuous processing... Press Ctrl+C to stop.\")
        processor.start_processing()

if __name__ == \"__main__\":
    main()"