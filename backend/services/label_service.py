import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid
from label_models import *
import httpx
import json

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/bigmann')
client = AsyncIOMotorClient(MONGO_URL)
db = client.bigmann  # Explicitly specify database name

class LabelManagementService:
    """Comprehensive service for commercial record label operations"""
    
    def __init__(self):
        # Database collections
        self.artists = db.artists
        self.contracts = db.artist_contracts
        self.demos = db.demo_submissions
        self.projects = db.recording_projects
        self.studios = db.recording_studios
        self.campaigns = db.marketing_campaigns
        self.press_releases = db.press_releases
        self.transactions = db.financial_transactions
        self.royalty_statements = db.royalty_statements
        self.analytics = db.artist_analytics
        self.scouts = db.talent_scouts
    
    # ===== ARTIST MANAGEMENT =====
    
    async def create_artist(self, artist_data: ArtistCreate, created_by: str) -> Dict[str, Any]:
        """Create a new artist profile"""
        artist = ArtistProfile(
            **artist_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.artists.insert_one(artist.dict())
        
        # Log activity
        await self._log_label_activity(
            created_by, 
            "artist_created", 
            "artist", 
            artist.id, 
            {"stage_name": artist.stage_name, "email": artist.email}
        )
        
        return {
            "success": True,
            "artist_id": artist.id,
            "message": f"Artist {artist.stage_name} created successfully"
        }
    
    async def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Get artist profile by ID"""
        artist = await self.artists.find_one({"id": artist_id})
        if artist:
            artist.pop("_id", None)
            
            # Get artist's contracts
            contracts = await self.contracts.find({"artist_id": artist_id}).to_list(length=None)
            for contract in contracts:
                contract.pop("_id", None)
            
            # Get active projects
            projects = await self.projects.find({"artist_id": artist_id}).to_list(length=None)
            for project in projects:
                project.pop("_id", None)
            
            artist["contracts"] = contracts
            artist["projects"] = projects
            
        return artist
    
    async def update_artist(self, artist_id: str, update_data: ArtistUpdate, updated_by: str) -> Dict[str, Any]:
        """Update artist profile"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.artists.update_one(
            {"id": artist_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count:
            await self._log_label_activity(
                updated_by, 
                "artist_updated", 
                "artist", 
                artist_id, 
                update_dict
            )
            return {"success": True, "message": "Artist updated successfully"}
        
        return {"success": False, "message": "Artist not found or no changes made"}
    
    async def get_artist_roster(self, status: Optional[ArtistStatus] = None, 
                               genre: Optional[str] = None, 
                               limit: int = 50) -> List[Dict[str, Any]]:
        """Get artist roster with filtering"""
        query = {}
        if status:
            query["status"] = status.value
        if genre:
            query["genres"] = {"$in": [genre]}
        
        artists = await self.artists.find(query).limit(limit).to_list(length=None)
        for artist in artists:
            artist.pop("_id", None)
        
        return artists
    
    # ===== CONTRACT MANAGEMENT =====
    
    async def create_contract(self, contract_data: ContractCreate, created_by: str) -> Dict[str, Any]:
        """Create a new artist contract"""
        contract = ArtistContract(
            **contract_data.dict(),
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.contracts.insert_one(contract.dict())
        
        # Update artist status if this is their first recording contract
        if contract.contract_type == ContractType.RECORDING:
            await self.artists.update_one(
                {"id": contract.artist_id},
                {"$set": {"status": ArtistStatus.ACTIVE, "signed_date": datetime.utcnow()}}
            )
        
        await self._log_label_activity(
            created_by, 
            "contract_created", 
            "contract", 
            contract.id, 
            {"artist_id": contract.artist_id, "type": contract.contract_type.value}
        )
        
        return {
            "success": True,
            "contract_id": contract.id,
            "message": "Contract created successfully"
        }
    
    async def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID"""
        contract = await self.contracts.find_one({"id": contract_id})
        if contract:
            contract.pop("_id", None)
            
            # Get associated artist info
            artist = await self.artists.find_one({"id": contract["artist_id"]})
            if artist:
                contract["artist_info"] = {
                    "stage_name": artist.get("stage_name"),
                    "real_name": artist.get("real_name"),
                    "email": artist.get("email")
                }
        
        return contract
    
    # ===== A&R MANAGEMENT =====
    
    async def submit_demo(self, demo_data: DemoSubmissionCreate) -> Dict[str, Any]:
        """Process a new demo submission"""
        demo = DemoSubmission(
            **demo_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.demos.insert_one(demo.dict())
        
        # Notify A&R team (implement email/slack notification)
        await self._notify_ar_team_new_demo(demo)
        
        return {
            "success": True,
            "submission_id": demo.id,
            "message": "Demo submitted successfully. You will receive feedback within 2-3 weeks."
        }
    
    async def evaluate_demo(self, demo_id: str, evaluator: str, 
                           score: float, notes: str, status: DemoStatus) -> Dict[str, Any]:
        """Evaluate a demo submission"""
        update_data = {
            "assigned_ar": evaluator,
            "evaluation_score": score,
            "evaluation_notes": notes,
            "status": status.value,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.demos.update_one(
            {"id": demo_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            # Send feedback to artist
            demo = await self.demos.find_one({"id": demo_id})
            if demo:
                await self._send_demo_feedback(demo, status, notes)
            
            await self._log_label_activity(
                evaluator, 
                "demo_evaluated", 
                "demo", 
                demo_id, 
                {"score": score, "status": status.value}
            )
            
            return {"success": True, "message": "Demo evaluation completed"}
        
        return {"success": False, "message": "Demo not found"}
    
    async def get_demo_submissions(self, status: Optional[DemoStatus] = None, 
                                  assigned_ar: Optional[str] = None,
                                  limit: int = 50) -> List[Dict[str, Any]]:
        """Get demo submissions with filtering"""
        query = {}
        if status:
            query["status"] = status.value
        if assigned_ar:
            query["assigned_ar"] = assigned_ar
        
        demos = await self.demos.find(query).limit(limit).to_list(length=None)
        for demo in demos:
            demo.pop("_id", None)
        
        return demos
    
    # ===== STUDIO & PRODUCTION MANAGEMENT =====
    
    async def create_recording_project(self, project_data: ProjectCreate, created_by: str) -> Dict[str, Any]:
        """Create a new recording project"""
        project = RecordingProject(
            **project_data.dict(),
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.projects.insert_one(project.dict())
        
        await self._log_label_activity(
            created_by, 
            "project_created", 
            "project", 
            project.id, 
            {"title": project.title, "artist_id": project.artist_id}
        )
        
        return {
            "success": True,
            "project_id": project.id,
            "message": f"Recording project '{project.title}' created successfully"
        }
    
    async def update_project_status(self, project_id: str, status: ProjectStatus, 
                                   updated_by: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update recording project status"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow()
        }
        if notes:
            update_data["notes"] = notes
        
        result = await self.projects.update_one(
            {"id": project_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            await self._log_label_activity(
                updated_by, 
                "project_status_updated", 
                "project", 
                project_id, 
                {"status": status.value, "notes": notes}
            )
            return {"success": True, "message": "Project status updated"}
        
        return {"success": False, "message": "Project not found"}
    
    async def add_studio(self, studio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a recording studio to the database"""
        studio = RecordingStudio(**studio_data)
        result = await self.studios.insert_one(studio.dict())
        
        return {
            "success": True,
            "studio_id": studio.id,
            "message": f"Studio '{studio.name}' added successfully"
        }
    
    async def get_available_studios(self, date_range: Dict[str, date]) -> List[Dict[str, Any]]:
        """Get available studios for booking"""
        # Simplified - in production would check actual availability
        studios = await self.studios.find({"active": {"$ne": False}}).to_list(length=None)
        for studio in studios:
            studio.pop("_id", None)
        
        return studios
    
    # ===== MARKETING CAMPAIGN MANAGEMENT =====
    
    async def create_marketing_campaign(self, campaign_data: CampaignCreate, created_by: str) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        campaign = MarketingCampaign(
            **campaign_data.dict(),
            campaign_manager=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.campaigns.insert_one(campaign.dict())
        
        await self._log_label_activity(
            created_by, 
            "campaign_created", 
            "campaign", 
            campaign.id, 
            {"name": campaign.name, "artist_id": campaign.artist_id}
        )
        
        return {
            "success": True,
            "campaign_id": campaign.id,
            "message": f"Marketing campaign '{campaign.name}' created successfully"
        }
    
    async def update_campaign_performance(self, campaign_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign performance metrics"""
        update_data = {
            **metrics,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.campaigns.update_one(
            {"id": campaign_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return {"success": True, "message": "Campaign metrics updated"}
        
        return {"success": False, "message": "Campaign not found"}
    
    async def create_press_release(self, pr_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a press release"""
        press_release = PressRelease(
            **pr_data,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.press_releases.insert_one(press_release.dict())
        
        return {
            "success": True,
            "pr_id": press_release.id,
            "message": f"Press release '{press_release.headline}' created successfully"
        }
    
    # ===== FINANCIAL MANAGEMENT =====
    
    async def create_transaction(self, transaction_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a financial transaction"""
        transaction = FinancialTransaction(
            **transaction_data,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.transactions.insert_one(transaction.dict())
        
        # Update recoupment tracking if applicable
        if transaction.recoupable:
            await self._update_recoupment_tracking(transaction.artist_id, transaction.amount)
        
        await self._log_label_activity(
            created_by, 
            "transaction_created", 
            "transaction", 
            transaction.id, 
            {"type": transaction.transaction_type.value, "amount": transaction.amount}
        )
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "message": "Transaction recorded successfully"
        }
    
    async def generate_royalty_statement(self, artist_id: str, period_start: date, 
                                       period_end: date, created_by: str) -> Dict[str, Any]:
        """Generate a royalty statement for an artist"""
        # Get streaming and sales data for the period
        streaming_data = await self._get_streaming_data(artist_id, period_start, period_end)
        sales_data = await self._get_sales_data(artist_id, period_start, period_end)
        
        # Get artist's contract for royalty calculations
        contract = await self.contracts.find_one({
            "artist_id": artist_id, 
            "contract_type": ContractType.RECORDING,
            "status": ContractStatus.ACTIVE
        })
        
        if not contract:
            return {"success": False, "message": "No active recording contract found"}
        
        # Calculate royalties
        royalty_calculations = self._calculate_royalties(streaming_data, sales_data, contract)
        
        statement = RoyaltyStatement(
            artist_id=artist_id,
            contract_id=contract["id"],
            statement_period_start=period_start,
            statement_period_end=period_end,
            streaming_data=streaming_data,
            digital_sales=sales_data,
            **royalty_calculations,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        result = await self.royalty_statements.insert_one(statement.dict())
        
        return {
            "success": True,
            "statement_id": statement.id,
            "net_payable": statement.net_payable,
            "message": "Royalty statement generated successfully"
        }
    
    # ===== ANALYTICS AND REPORTING =====
    
    async def generate_artist_analytics(self, artist_id: str, period_start: date, 
                                       period_end: date, generated_by: str) -> Dict[str, Any]:
        """Generate comprehensive analytics for an artist"""
        # Collect data from various sources
        streaming_data = await self._collect_streaming_analytics(artist_id, period_start, period_end)
        social_data = await self._collect_social_analytics(artist_id, period_start, period_end)
        financial_data = await self._collect_financial_analytics(artist_id, period_start, period_end)
        
        analytics = ArtistAnalytics(
            artist_id=artist_id,
            reporting_period_start=period_start,
            reporting_period_end=period_end,
            **streaming_data,
            **social_data,
            **financial_data,
            generated_by=generated_by,
            generated_at=datetime.utcnow()
        )
        
        result = await self.analytics.insert_one(analytics.dict())
        
        return {
            "success": True,
            "analytics_id": analytics.id,
            "total_streams": analytics.total_streams,
            "total_revenue": analytics.total_revenue,
            "message": "Artist analytics generated successfully"
        }
    
    async def generate_label_dashboard(self, period_start: date, period_end: date, 
                                     generated_by: str) -> Dict[str, Any]:
        """Generate comprehensive label dashboard"""
        # Collect overall label metrics
        total_artists = await self.artists.count_documents({"status": {"$ne": ArtistStatus.INACTIVE}})
        active_projects = await self.projects.count_documents({"status": {"$in": ["recording", "mixing", "mastering"]}})
        
        # Get top performers
        top_artists = await self._get_top_performing_artists(period_start, period_end)
        
        # Financial summary
        revenue_data = await self._get_label_revenue_summary(period_start, period_end)
        
        # A&R metrics
        ar_metrics = await self._get_ar_metrics(period_start, period_end)
        
        dashboard = LabelDashboard(
            reporting_period_start=period_start,
            reporting_period_end=period_end,
            total_artists=total_artists,
            active_projects=active_projects,
            top_artists=top_artists,
            **revenue_data,
            **ar_metrics,
            generated_by=generated_by,
            generated_at=datetime.utcnow()
        )
        
        return dashboard.dict()
    
    # ===== MUSIC INDUSTRY DATABASE INTEGRATION =====
    
    async def search_music_industry_contacts(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Search music industry contacts and databases"""
        # Integration with services like MusicBrainz, AllMusic, industry directories
        contacts = []
        
        # Mock implementation - in production, integrate with real databases
        if category in ["radio", "all"]:
            contacts.extend(await self._search_radio_contacts(query))
        
        if category in ["press", "all"]:
            contacts.extend(await self._search_press_contacts(query))
        
        if category in ["playlist", "all"]:
            contacts.extend(await self._search_playlist_contacts(query))
        
        if category in ["labels", "all"]:
            contacts.extend(await self._search_label_contacts(query))
        
        return contacts
    
    async def get_industry_trends(self) -> Dict[str, Any]:
        """Get current music industry trends and insights"""
        # Integration with music analytics services
        trends = {
            "trending_genres": await self._get_trending_genres(),
            "popular_artists": await self._get_popular_artists(),
            "playlist_trends": await self._get_playlist_trends(),
            "market_insights": await self._get_market_insights(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return trends
    
    # ===== PRIVATE HELPER METHODS =====
    
    async def _log_label_activity(self, user_id: str, action: str, resource_type: str, 
                                resource_id: str, details: Dict[str, Any]):
        """Log label management activities"""
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        
        await db.label_activities.insert_one(activity)
    
    async def _notify_ar_team_new_demo(self, demo: DemoSubmission):
        """Notify A&R team of new demo submission"""
        # Implementation would send email/Slack notification
        pass
    
    async def _send_demo_feedback(self, demo: Dict[str, Any], status: DemoStatus, notes: str):
        """Send feedback to demo submitter"""
        # Implementation would send email with feedback
        pass
    
    async def _update_recoupment_tracking(self, artist_id: str, amount: float):
        """Update artist recoupment tracking"""
        # Implementation would update recoupment balances
        pass
    
    async def _get_streaming_data(self, artist_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get streaming data from various platforms"""
        # Mock implementation - integrate with Spotify API, Apple Music API, etc.
        return {
            "spotify_streams": 150000,
            "apple_music_streams": 75000,
            "youtube_streams": 200000,
            "total_streams": 425000
        }
    
    async def _get_sales_data(self, artist_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get sales data"""
        # Mock implementation
        return {
            "digital_downloads": 5000,
            "physical_sales": 500,
            "total_sales": 5500
        }
    
    def _calculate_royalties(self, streaming_data: Dict[str, Any], 
                           sales_data: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate royalty payments"""
        # Simplified calculation - in production would be more complex
        royalty_rate = contract.get("royalty_rate", 0.15)  # 15% default
        
        # Estimate revenue (simplified)
        streaming_revenue = streaming_data.get("total_streams", 0) * 0.003  # $0.003 per stream
        sales_revenue = sales_data.get("total_sales", 0) * 0.99  # $0.99 per download
        
        gross_revenue = streaming_revenue + sales_revenue
        artist_share = gross_revenue * royalty_rate
        label_share = gross_revenue * (1 - royalty_rate)
        
        return {
            "gross_revenue": gross_revenue,
            "artist_share": artist_share,
            "label_share": label_share,
            "net_payable": artist_share  # Simplified - would account for recoupment
        }
    
    # Mock implementations for industry database searches
    async def _search_radio_contacts(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"name": "KCRW Music Director", "email": "music@kcrw.com", "type": "radio", "genre": "indie"},
            {"name": "BBC Radio 1", "email": "newmusic@bbc.co.uk", "type": "radio", "genre": "pop"}
        ]
    
    async def _search_press_contacts(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"name": "Pitchfork", "email": "tips@pitchfork.com", "type": "press", "focus": "indie music"},
            {"name": "Rolling Stone", "email": "news@rollingstone.com", "type": "press", "focus": "all genres"}
        ]
    
    async def _search_playlist_contacts(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"name": "Spotify New Music Friday", "contact": "Spotify for Artists", "type": "playlist", "followers": "2.8M"},
            {"name": "Apple Music Breakthrough", "contact": "Apple Music Connect", "type": "playlist", "followers": "1.5M"}
        ]
    
    async def _search_label_contacts(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"name": "Sub Pop Records", "email": "info@subpop.com", "type": "label", "genre": "indie rock"},
            {"name": "Domino Records", "email": "info@dominorecordco.com", "type": "label", "genre": "indie"}
        ]
    
    async def _get_trending_genres(self) -> List[str]:
        return ["hyperpop", "bedroom pop", "trap", "drill", "afrobeats"]
    
    async def _get_popular_artists(self) -> List[Dict[str, str]]:
        return [
            {"name": "Artist Name", "genre": "pop", "monthly_listeners": "5.2M"},
            {"name": "Another Artist", "genre": "hip-hop", "monthly_listeners": "3.8M"}
        ]
    
    async def _get_playlist_trends(self) -> Dict[str, Any]:
        return {
            "top_playlists": ["New Music Friday", "RapCaviar", "Today's Top Hits"],
            "trending_moods": ["chill", "workout", "focus"]
        }
    
    async def _get_market_insights(self) -> Dict[str, Any]:
        return {
            "streaming_growth": "12% YoY",
            "vinyl_sales": "23% increase",
            "top_markets": ["US", "UK", "Germany", "Japan"]
        }
    
    async def _collect_streaming_analytics(self, artist_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        # Mock implementation
        return {
            "total_streams": 500000,
            "monthly_listeners": 85000,
            "spotify_data": {"streams": 250000, "listeners": 45000},
            "apple_music_data": {"streams": 150000, "listeners": 25000},
            "youtube_data": {"streams": 100000, "listeners": 15000}
        }
    
    async def _collect_social_analytics(self, artist_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        # Mock implementation
        return {
            "social_followers": 125000,
            "engagement_rate": 4.2,
            "instagram_data": {"followers": 75000, "engagement": 5.1},
            "tiktok_data": {"followers": 40000, "engagement": 8.5},
            "twitter_data": {"followers": 10000, "engagement": 2.8}
        }
    
    async def _collect_financial_analytics(self, artist_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        # Mock implementation
        return {
            "total_revenue": 15000.00,
            "revenue_breakdown": {
                "streaming": 8000.00,
                "downloads": 3000.00,
                "merchandise": 2500.00,
                "sync": 1500.00
            }
        }
    
    async def _get_top_performing_artists(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        # Mock implementation
        return [
            {"artist_id": "artist1", "stage_name": "Top Artist", "streams": 1000000, "revenue": 25000},
            {"artist_id": "artist2", "stage_name": "Rising Star", "streams": 750000, "revenue": 18000}
        ]
    
    async def _get_label_revenue_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        # Mock implementation
        return {
            "total_revenue": 150000.00,
            "revenue_breakdown": {
                "streaming": 80000.00,
                "sales": 40000.00,
                "sync": 20000.00,
                "merchandise": 10000.00
            },
            "expense_breakdown": {
                "marketing": 25000.00,
                "recording": 20000.00,
                "advances": 15000.00,
                "overhead": 10000.00
            },
            "profit_loss": 80000.00
        }
    
    async def _get_ar_metrics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        # Mock implementation
        return {
            "demos_received": 150,
            "artists_signed": 2,
            "conversion_rate": 1.3
        }