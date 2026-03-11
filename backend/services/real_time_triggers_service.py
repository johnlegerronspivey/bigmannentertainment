"""
Real-Time Triggers Service
Big Mann Entertainment Platform - pDOOH Integration

This service manages real-time triggers for dynamic creative optimization
including weather, sports events, and custom triggers.
"""

import uuid
import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherCondition(str, Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    FOGGY = "foggy"

class SportType(str, Enum):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    BASEBALL = "baseball"
    HOCKEY = "hockey"
    SOCCER = "soccer"
    TENNIS = "tennis"

class EventType(str, Enum):
    CONCERT = "concert"
    FESTIVAL = "festival"
    SPORTS_GAME = "sports_game"
    CONFERENCE = "conference"
    EXHIBITION = "exhibition"

# Pydantic Models
class WeatherTrigger(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature: float
    condition: WeatherCondition
    humidity: float
    wind_speed: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SportsEventTrigger(BaseModel):
    event_id: str
    sport: SportType
    teams: List[str]
    venue: str
    start_time: datetime
    status: str  # scheduled, live, completed
    score: Optional[Dict[str, int]] = None
    location: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomEventTrigger(BaseModel):
    event_id: str
    name: str
    event_type: EventType
    location: str
    start_time: datetime
    end_time: datetime
    attendance_estimate: Optional[int] = None
    related_artists: List[str] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TriggerRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    trigger_type: str  # "weather", "sports", "event", "custom"
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    active: bool = True
    priority: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RealTimeTriggersService:
    """Service for managing real-time triggers and dynamic creative optimization"""
    
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        self.espn_api_key = os.getenv("ESPN_API_KEY", "demo_key")
        self.eventbrite_api_key = os.getenv("EVENTBRITE_API_KEY", "demo_key")
        
        self.trigger_rules = {}
        self.active_triggers = {}
        self.trigger_history = []
        
        # Cache for API responses
        self.weather_cache = {}
        self.sports_cache = {}
        self.events_cache = {}
        
        logger.info("Real-Time Triggers Service initialized")
    
    async def get_weather_data(self, latitude: float, longitude: float, location_name: str = "") -> WeatherTrigger:
        """Get current weather data for a location"""
        try:
            cache_key = f"{latitude},{longitude}"
            
            # Check cache first (valid for 10 minutes)
            if cache_key in self.weather_cache:
                cached_data, timestamp = self.weather_cache[cache_key]
                if datetime.now(timezone.utc) - timestamp < timedelta(minutes=10):
                    return cached_data
            
            # In production, this would call OpenWeatherMap API
            # For demo, generate realistic weather data
            import random
            
            conditions = list(WeatherCondition)
            condition = random.choice(conditions)
            
            # Temperature ranges based on condition
            temp_ranges = {
                WeatherCondition.SUNNY: (15, 30),
                WeatherCondition.CLOUDY: (10, 25),
                WeatherCondition.RAINY: (5, 20),
                WeatherCondition.SNOWY: (-10, 5),
                WeatherCondition.STORMY: (10, 25),
                WeatherCondition.FOGGY: (8, 18)
            }
            
            temp_range = temp_ranges.get(condition, (10, 25))
            temperature = round(random.uniform(*temp_range), 1)
            
            weather_trigger = WeatherTrigger(
                location=location_name or f"Location {latitude:.2f},{longitude:.2f}",
                latitude=latitude,
                longitude=longitude,
                temperature=temperature,
                condition=condition,
                humidity=round(random.uniform(30, 90), 1),
                wind_speed=round(random.uniform(0, 25), 1)
            )
            
            # Cache the result
            self.weather_cache[cache_key] = (weather_trigger, datetime.now(timezone.utc))
            
            logger.info(f"Weather data retrieved for {location_name}: {condition.value}, {temperature}°C")
            return weather_trigger
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            # Return default weather data
            return WeatherTrigger(
                location=location_name or "Unknown Location",
                latitude=latitude,
                longitude=longitude,
                temperature=20.0,
                condition=WeatherCondition.SUNNY,
                humidity=50.0,
                wind_speed=5.0
            )
    
    async def get_sports_events(self, location: str, date: datetime = None) -> List[SportsEventTrigger]:
        """Get sports events for a location and date"""
        try:
            if date is None:
                date = datetime.now(timezone.utc)
            
            cache_key = f"{location}_{date.date()}"
            
            # Check cache first (valid for 1 hour)
            if cache_key in self.sports_cache:
                cached_data, timestamp = self.sports_cache[cache_key]
                if datetime.now(timezone.utc) - timestamp < timedelta(hours=1):
                    return cached_data
            
            # In production, this would call ESPN API or similar
            # For demo, generate realistic sports events
            import random
            
            sports = list(SportType)
            events = []
            
            # Generate 0-3 events per day
            num_events = random.randint(0, 3)
            
            for i in range(num_events):
                sport = random.choice(sports)
                
                # Generate teams based on sport
                team_pools = {
                    SportType.FOOTBALL: ["Chiefs", "Cowboys", "Patriots", "Packers", "49ers"],
                    SportType.BASKETBALL: ["Lakers", "Warriors", "Celtics", "Bulls", "Heat"],
                    SportType.BASEBALL: ["Yankees", "Dodgers", "Red Sox", "Giants", "Cubs"],
                    SportType.HOCKEY: ["Rangers", "Bruins", "Kings", "Blackhawks", "Lightning"],
                    SportType.SOCCER: ["LAFC", "Atlanta United", "Seattle Sounders", "NYC FC"],
                    SportType.TENNIS: ["Djokovic", "Nadal", "Federer", "Serena", "Osaka"]
                }
                
                teams = random.sample(team_pools.get(sport, ["Team A", "Team B"]), 2)
                
                event = SportsEventTrigger(
                    event_id=f"event_{uuid.uuid4().hex[:8]}",
                    sport=sport,
                    teams=teams,
                    venue=f"{location} {sport.value.title()} Arena",
                    start_time=date + timedelta(hours=random.randint(12, 22)),
                    status=random.choice(["scheduled", "live", "completed"]),
                    score={teams[0]: random.randint(0, 5), teams[1]: random.randint(0, 5)} if random.choice([True, False]) else None,
                    location=location
                )
                events.append(event)
            
            # Cache the result
            self.sports_cache[cache_key] = (events, datetime.now(timezone.utc))
            
            logger.info(f"Sports events retrieved for {location}: {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error getting sports events: {e}")
            return []
    
    async def get_local_events(self, location: str, radius_km: int = 25, date: datetime = None) -> List[CustomEventTrigger]:
        """Get local events for a location"""
        try:
            if date is None:
                date = datetime.now(timezone.utc)
            
            cache_key = f"{location}_{radius_km}_{date.date()}"
            
            # Check cache first (valid for 30 minutes)
            if cache_key in self.events_cache:
                cached_data, timestamp = self.events_cache[cache_key]
                if datetime.now(timezone.utc) - timestamp < timedelta(minutes=30):
                    return cached_data
            
            # In production, this would call Eventbrite API or similar
            # For demo, generate realistic local events
            import random
            
            event_types = list(EventType)
            events = []
            
            # Generate 1-5 events
            num_events = random.randint(1, 5)
            
            event_names = {
                EventType.CONCERT: ["Summer Music Festival", "Rock Concert", "Jazz Night", "Classical Performance"],
                EventType.FESTIVAL: ["Food Festival", "Art Fair", "Cultural Celebration", "Beer Festival"],
                EventType.SPORTS_GAME: ["Local Championship", "Community Tournament", "Sports Festival"],
                EventType.CONFERENCE: ["Tech Conference", "Business Summit", "Industry Meetup"],
                EventType.EXHIBITION: ["Art Exhibition", "Car Show", "Trade Show", "Museum Opening"]
            }
            
            for i in range(num_events):
                event_type = random.choice(event_types)
                name = random.choice(event_names.get(event_type, ["Local Event"]))
                
                start_time = date + timedelta(hours=random.randint(6, 48))
                duration_hours = random.randint(2, 12)
                
                event = CustomEventTrigger(
                    event_id=f"event_{uuid.uuid4().hex[:8]}",
                    name=name,
                    event_type=event_type,
                    location=f"{location} Event Center",
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=duration_hours),
                    attendance_estimate=random.randint(100, 10000),
                    related_artists=["Artist " + str(random.randint(1, 100)) for _ in range(random.randint(0, 3))],
                    metadata={
                        "price_range": f"${random.randint(10, 200)}-${random.randint(200, 500)}",
                        "age_restriction": random.choice(["All Ages", "18+", "21+"]),
                        "genre": random.choice(["Pop", "Rock", "Hip-Hop", "Electronic", "Classical"])
                    }
                )
                events.append(event)
            
            # Cache the result
            self.events_cache[cache_key] = (events, datetime.now(timezone.utc))
            
            logger.info(f"Local events retrieved for {location}: {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error getting local events: {e}")
            return []
    
    async def create_trigger_rule(self, rule_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new trigger rule"""
        try:
            # Validate rule data
            required_fields = ['name', 'trigger_type', 'conditions', 'actions']
            missing_fields = [field for field in required_fields if field not in rule_data]
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            rule = TriggerRule(
                name=rule_data['name'],
                trigger_type=rule_data['trigger_type'],
                conditions=rule_data['conditions'],
                actions=rule_data['actions'],
                active=rule_data.get('active', True),
                priority=rule_data.get('priority', 1)
            )
            
            self.trigger_rules[rule.id] = rule
            
            logger.info(f"Created trigger rule {rule.id} for user {user_id}")
            
            return {
                "success": True,
                "rule_id": rule.id,
                "rule": rule.dict(),
                "message": "Trigger rule created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating trigger rule: {e}")
            return {"success": False, "error": str(e)}
    
    async def evaluate_triggers(self, campaign_id: str, location: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Evaluate all active triggers for a campaign and location"""
        try:
            triggered_conditions = []
            creative_variants = {}
            
            # Get current weather
            weather = await self.get_weather_data(latitude, longitude, location)
            
            # Get sports events
            sports_events = await self.get_sports_events(location)
            
            # Get local events
            local_events = await self.get_local_events(location)
            
            # Evaluate weather-based triggers
            weather_triggers = await self._evaluate_weather_triggers(weather)
            triggered_conditions.extend(weather_triggers)
            
            # Evaluate sports-based triggers
            sports_triggers = await self._evaluate_sports_triggers(sports_events)
            triggered_conditions.extend(sports_triggers)
            
            # Evaluate event-based triggers
            event_triggers = await self._evaluate_event_triggers(local_events)
            triggered_conditions.extend(event_triggers)
            
            # Evaluate custom triggers
            custom_triggers = await self._evaluate_custom_triggers(campaign_id, location)
            triggered_conditions.extend(custom_triggers)
            
            # Determine creative variants to use
            if triggered_conditions:
                # Sort by priority and select highest priority triggers
                triggered_conditions.sort(key=lambda x: x.get('priority', 1), reverse=True)
                creative_variants = self._select_creative_variants(triggered_conditions)
            
            result = {
                "success": True,
                "campaign_id": campaign_id,
                "location": location,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "triggered_conditions": triggered_conditions,
                "creative_variants": creative_variants,
                "context_data": {
                    "weather": weather.dict(),
                    "sports_events": [event.dict() for event in sports_events],
                    "local_events": [event.dict() for event in local_events]
                }
            }
            
            # Store in history
            self.trigger_history.append(result)
            
            logger.info(f"Evaluated triggers for campaign {campaign_id}: {len(triggered_conditions)} conditions triggered")
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating triggers: {e}")
            return {"success": False, "error": str(e)}
    
    async def _evaluate_weather_triggers(self, weather: WeatherTrigger) -> List[Dict[str, Any]]:
        """Evaluate weather-based trigger conditions"""
        triggers = []
        
        # Temperature-based triggers
        if weather.temperature > 25:
            triggers.append({
                "type": "weather",
                "condition": "hot_weather",
                "value": weather.temperature,
                "priority": 2,
                "creative_suggestions": ["summer_themes", "cold_drinks", "outdoor_activities"]
            })
        elif weather.temperature < 5:
            triggers.append({
                "type": "weather",
                "condition": "cold_weather",
                "value": weather.temperature,
                "priority": 2,
                "creative_suggestions": ["winter_themes", "warm_clothing", "hot_drinks"]
            })
        
        # Condition-based triggers
        if weather.condition == WeatherCondition.RAINY:
            triggers.append({
                "type": "weather",
                "condition": "rainy",
                "value": weather.condition.value,
                "priority": 3,
                "creative_suggestions": ["indoor_activities", "umbrellas", "cozy_themes"]
            })
        elif weather.condition == WeatherCondition.SUNNY:
            triggers.append({
                "type": "weather",
                "condition": "sunny",
                "value": weather.condition.value,
                "priority": 1,
                "creative_suggestions": ["outdoor_activities", "sunglasses", "bright_themes"]
            })
        
        return triggers
    
    async def _evaluate_sports_triggers(self, sports_events: List[SportsEventTrigger]) -> List[Dict[str, Any]]:
        """Evaluate sports-based trigger conditions"""
        triggers = []
        
        for event in sports_events:
            if event.status == "live":
                triggers.append({
                    "type": "sports",
                    "condition": "live_game",
                    "value": {
                        "sport": event.sport.value,
                        "teams": event.teams,
                        "score": event.score
                    },
                    "priority": 4,
                    "creative_suggestions": ["sports_themes", "team_colors", "game_excitement"]
                })
            elif event.status == "scheduled" and event.start_time <= datetime.now(timezone.utc) + timedelta(hours=2):
                triggers.append({
                    "type": "sports",
                    "condition": "upcoming_game",
                    "value": {
                        "sport": event.sport.value,
                        "teams": event.teams,
                        "start_time": event.start_time.isoformat()
                    },
                    "priority": 3,
                    "creative_suggestions": ["pre_game_excitement", "team_merchandise", "venue_directions"]
                })
        
        return triggers
    
    async def _evaluate_event_triggers(self, local_events: List[CustomEventTrigger]) -> List[Dict[str, Any]]:
        """Evaluate event-based trigger conditions"""
        triggers = []
        
        now = datetime.now(timezone.utc)
        
        for event in local_events:
            if event.start_time <= now <= event.end_time:
                triggers.append({
                    "type": "event",
                    "condition": "live_event",
                    "value": {
                        "name": event.name,
                        "type": event.event_type.value,
                        "attendance": event.attendance_estimate
                    },
                    "priority": 3,
                    "creative_suggestions": ["event_themes", "live_excitement", "social_sharing"]
                })
            elif event.start_time <= now + timedelta(hours=4):
                triggers.append({
                    "type": "event",
                    "condition": "upcoming_event",
                    "value": {
                        "name": event.name,
                        "type": event.event_type.value,
                        "start_time": event.start_time.isoformat()
                    },
                    "priority": 2,
                    "creative_suggestions": ["event_promotion", "ticket_availability", "artist_spotlight"]
                })
        
        return triggers
    
    async def _evaluate_custom_triggers(self, campaign_id: str, location: str) -> List[Dict[str, Any]]:
        """Evaluate custom trigger conditions"""
        triggers = []
        
        # Time-based triggers
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        if 7 <= hour <= 9:  # Morning commute
            triggers.append({
                "type": "custom",
                "condition": "morning_commute",
                "value": {"hour": hour},
                "priority": 2,
                "creative_suggestions": ["coffee_themes", "morning_energy", "commuter_friendly"]
            })
        elif 17 <= hour <= 19:  # Evening commute
            triggers.append({
                "type": "custom",
                "condition": "evening_commute",
                "value": {"hour": hour},
                "priority": 2,
                "creative_suggestions": ["entertainment", "dining", "relaxation"]
            })
        elif 21 <= hour <= 23:  # Nightlife
            triggers.append({
                "type": "custom",
                "condition": "nightlife_hours",
                "value": {"hour": hour},
                "priority": 3,
                "creative_suggestions": ["nightlife", "bars_clubs", "late_night_entertainment"]
            })
        
        # Weekend vs weekday
        if now.weekday() >= 5:  # Weekend
            triggers.append({
                "type": "custom",
                "condition": "weekend",
                "value": {"day": "weekend"},
                "priority": 1,
                "creative_suggestions": ["leisure_activities", "family_time", "weekend_events"]
            })
        
        return triggers
    
    def _select_creative_variants(self, triggered_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select appropriate creative variants based on triggered conditions"""
        creative_variants = {
            "primary_variant": "default",
            "overlay_elements": [],
            "color_scheme": "default",
            "messaging": "default",
            "call_to_action": "default"
        }
        
        # Prioritize by condition priority
        for condition in triggered_conditions:
            condition_type = condition.get("condition")
            suggestions = condition.get("creative_suggestions", [])
            
            if condition_type == "hot_weather" and "summer_themes" in suggestions:
                creative_variants["primary_variant"] = "summer"
                creative_variants["color_scheme"] = "warm"
                creative_variants["messaging"] = "Beat the heat with cool music!"
            elif condition_type == "rainy" and "indoor_activities" in suggestions:
                creative_variants["primary_variant"] = "cozy"
                creative_variants["color_scheme"] = "cool"
                creative_variants["messaging"] = "Perfect indoor vibes!"
            elif condition_type == "live_game" and "sports_themes" in suggestions:
                creative_variants["primary_variant"] = "sports"
                creative_variants["overlay_elements"].append("live_score")
                creative_variants["messaging"] = "Game day energy!"
            elif condition_type == "nightlife_hours":
                creative_variants["primary_variant"] = "nightlife"
                creative_variants["color_scheme"] = "vibrant"
                creative_variants["messaging"] = "Turn up the night!"
            
            # Add overlay elements
            if "live_excitement" in suggestions:
                creative_variants["overlay_elements"].append("live_indicator")
            if "social_sharing" in suggestions:
                creative_variants["overlay_elements"].append("social_cta")
        
        return creative_variants
    
    async def get_trigger_history(self, campaign_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get trigger history for a campaign"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            relevant_history = [
                entry for entry in self.trigger_history
                if (entry.get("campaign_id") == campaign_id and 
                    datetime.fromisoformat(entry["timestamp"]) >= cutoff_time)
            ]
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "history_count": len(relevant_history),
                "trigger_history": relevant_history,
                "summary": self._summarize_trigger_history(relevant_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting trigger history: {e}")
            return {"success": False, "error": str(e)}
    
    def _summarize_trigger_history(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize trigger history data"""
        if not history:
            return {"total_triggers": 0}
        
        trigger_counts = {}
        total_triggers = 0
        
        for entry in history:
            conditions = entry.get("triggered_conditions", [])
            total_triggers += len(conditions)
            
            for condition in conditions:
                condition_type = condition.get("condition", "unknown")
                trigger_counts[condition_type] = trigger_counts.get(condition_type, 0) + 1
        
        return {
            "total_triggers": total_triggers,
            "avg_triggers_per_evaluation": round(total_triggers / len(history), 2),
            "most_common_triggers": sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "evaluation_count": len(history)
        }

# Global instance
real_time_triggers_service = RealTimeTriggersService()