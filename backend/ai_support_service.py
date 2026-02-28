"""
AI Support Service for Advanced Support System
Provides AI-powered features including auto-tagging, FAQ suggestions, dispute analysis
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import os
from dotenv import load_dotenv

from llm_service import LlmChat, UserMessage

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AISupportService:
    """AI-powered support service using OpenAI GPT-4o and Claude Sonnet 4"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.claude_api_key = os.environ.get("CLAUDE_API_KEY")
        
        if not self.openai_api_key or not self.claude_api_key:
            raise ValueError("OpenAI and Claude API keys are required")
        
        # Initialize AI models
        self.openai_chat = None
        self.claude_chat = None
        
    async def initialize_ai_models(self):
        """Initialize AI chat models with session IDs"""
        try:
            # OpenAI GPT-4o for general support tasks
            openai_session_id = f"openai-support-{uuid.uuid4().hex[:8]}"
            self.openai_chat = LlmChat(
                api_key=self.openai_api_key,
                session_id=openai_session_id,
                system_message="You are an expert customer support AI assistant for Big Mann Entertainment, a music distribution and licensing platform. Help categorize tickets, suggest solutions, and provide helpful responses. Be concise and professional."
            ).with_model("openai", "gpt-4o")
            
            # Claude Sonnet 4 for complex reasoning and dispute analysis
            claude_session_id = f"claude-support-{uuid.uuid4().hex[:8]}"
            self.claude_chat = LlmChat(
                api_key=self.claude_api_key,
                session_id=claude_session_id,
                system_message="You are Claude, an advanced AI assistant specializing in dispute resolution and complex analysis for Big Mann Entertainment. Provide detailed analysis, evidence review, and reasoned recommendations for support disputes."
            ).with_model("anthropic", "claude-3-7-sonnet-20250219")
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {str(e)}")
            raise
    
    async def auto_categorize_ticket(self, title: str, description: str) -> Dict[str, Any]:
        """Auto-categorize support tickets using AI"""
        try:
            if not self.openai_chat:
                await self.initialize_ai_models()
            
            prompt = f"""
            Analyze this support ticket and provide categorization:
            
            Title: {title}
            Description: {description}
            
            Please provide:
            1. Category (one of: technical_support, licensing_dispute, royalty_issue, platform_bug, content_removal, payment_issue, account_access, general_inquiry)
            2. Priority (low, medium, high, critical)
            3. Tags (3-5 relevant keywords)
            4. Estimated resolution complexity (simple, moderate, complex)
            5. Suggested initial response
            
            Format as JSON:
            {{
                "category": "category_name",
                "priority": "priority_level", 
                "tags": ["tag1", "tag2", "tag3"],
                "complexity": "complexity_level",
                "suggested_response": "initial response text",
                "confidence": 0.95
            }}
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.openai_chat.send_message(user_message)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return {
                    "category": "general_inquiry",
                    "priority": "medium",
                    "tags": ["support", "assistance"],
                    "complexity": "moderate",
                    "suggested_response": "Thank you for contacting Big Mann Entertainment support. We have received your request and will respond shortly.",
                    "confidence": 0.5
                }
                
        except Exception as e:
            logger.error(f"Error in auto-categorization: {str(e)}")
            return {
                "category": "general_inquiry",
                "priority": "medium", 
                "tags": ["support"],
                "complexity": "moderate",
                "suggested_response": "Thank you for your support request. Our team will review it shortly.",
                "confidence": 0.0
            }
    
    async def generate_faq_suggestions(self, query: str, context: str = None) -> List[Dict[str, Any]]:
        """Generate FAQ article suggestions based on user query"""
        try:
            if not self.openai_chat:
                await self.initialize_ai_models()
            
            context_text = f"\nContext: {context}" if context else ""
            
            prompt = f"""
            Based on this user query, suggest 5 relevant FAQ topics for Big Mann Entertainment support:
            
            Query: {query}{context_text}
            
            Consider these common support areas:
            - Music distribution and licensing
            - Royalty payments and tracking
            - Platform integration issues
            - Content uploading and metadata
            - Account management
            - Copyright and DMCA
            - DAO governance and disputes
            
            For each suggestion, provide:
            1. FAQ title
            2. Brief answer (2-3 sentences)
            3. Relevance score (0.0-1.0)
            4. Category
            
            Format as JSON array:
            [
                {{
                    "title": "FAQ title",
                    "answer": "Brief answer",
                    "relevance": 0.95,
                    "category": "category_name"
                }}
            ]
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.openai_chat.send_message(user_message)
            
            import json
            try:
                suggestions = json.loads(response)
                return suggestions[:5]  # Limit to 5 suggestions
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Error generating FAQ suggestions: {str(e)}")
            return []
    
    async def analyze_dispute_evidence(self, dispute_description: str, evidence_summary: str, involved_parties: List[str]) -> Dict[str, Any]:
        """Analyze dispute evidence using Claude for complex reasoning"""
        try:
            if not self.claude_chat:
                await self.initialize_ai_models()
            
            prompt = f"""
            Analyze this support dispute for Big Mann Entertainment and provide detailed assessment:
            
            Dispute Description: {dispute_description}
            
            Evidence Summary: {evidence_summary}
            
            Involved Parties: {', '.join(involved_parties)}
            
            Please provide a comprehensive analysis including:
            
            1. Dispute Classification:
               - Type (licensing, royalty, copyright, platform, other)
               - Severity (minor, moderate, major, critical)
               - Legitimacy assessment (0.0-1.0 confidence)
            
            2. Evidence Evaluation:
               - Strength of evidence (weak, moderate, strong)
               - Key evidence points
               - Missing evidence or information needed
            
            3. Recommended Actions:
               - Immediate steps
               - Investigation requirements
               - Potential resolutions
               - Escalation recommendations
            
            4. Risk Assessment:
               - Business impact (low, medium, high)
               - Legal implications
               - Reputation risk
               - Financial exposure
            
            5. Timeline Recommendations:
               - Suggested response timeline
               - Resolution target
               - Milestones for follow-up
            
            Format as detailed JSON with reasoning for each assessment.
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.claude_chat.send_message(user_message)
            
            import json
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                # Return structured fallback
                return {
                    "dispute_classification": {
                        "type": "general",
                        "severity": "moderate", 
                        "legitimacy": 0.5
                    },
                    "evidence_evaluation": {
                        "strength": "moderate",
                        "key_points": ["Dispute requires detailed review"],
                        "missing_info": ["Additional documentation needed"]
                    },
                    "recommended_actions": {
                        "immediate": ["Review submitted evidence", "Contact involved parties"],
                        "investigation": ["Gather additional information"],
                        "resolutions": ["Standard mediation process"],
                        "escalation": ["Escalate if unresolved in 7 days"]
                    },
                    "risk_assessment": {
                        "business_impact": "medium",
                        "legal_implications": "Standard dispute resolution",
                        "reputation_risk": "low",
                        "financial_exposure": "minimal"
                    },
                    "timeline": {
                        "response": "24 hours",
                        "resolution_target": "7 days", 
                        "milestones": ["Initial review", "Evidence analysis", "Resolution attempt"]
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in dispute analysis: {str(e)}")
            return {"error": "Analysis failed", "message": str(e)}
    
    async def generate_automated_response(self, ticket_category: str, issue_description: str, user_context: Dict[str, Any] = None) -> str:
        """Generate automated response for common support issues"""
        try:
            if not self.openai_chat:
                await self.initialize_ai_models()
            
            context_info = ""
            if user_context:
                context_info = f"User Context: {user_context}"
            
            prompt = f"""
            Generate a helpful, professional automated response for this Big Mann Entertainment support request:
            
            Category: {ticket_category}
            Issue: {issue_description}
            {context_info}
            
            Guidelines:
            - Be empathetic and professional
            - Provide specific next steps when possible
            - Include relevant links or resources
            - Mention expected response times
            - Use Big Mann Entertainment branding appropriately
            
            Keep response concise but helpful (2-4 paragraphs max).
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.openai_chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating automated response: {str(e)}")
            return "Thank you for contacting Big Mann Entertainment support. We have received your request and will respond within 24 hours."
    
    async def extract_key_topics(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """Extract key topics and themes from conversation history"""
        try:
            if not self.openai_chat:
                await self.initialize_ai_models()
            
            # Format conversation for analysis
            conversation_text = ""
            for msg in conversation_history[-10:]:  # Last 10 messages
                speaker = msg.get("sender_type", "user")
                content = msg.get("content", "")
                conversation_text += f"{speaker}: {content}\n"
            
            prompt = f"""
            Analyze this support conversation and extract key topics, issues, and themes:
            
            Conversation:
            {conversation_text}
            
            Extract:
            1. Main topics discussed
            2. Specific issues mentioned
            3. Resolution status
            4. Next actions needed
            
            Return as JSON array of topics with importance scores:
            [
                {{
                    "topic": "topic name",
                    "importance": 0.8,
                    "category": "category"
                }}
            ]
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.openai_chat.send_message(user_message)
            
            import json
            try:
                topics = json.loads(response)
                return [topic["topic"] for topic in topics if topic.get("importance", 0) > 0.5]
            except json.JSONDecodeError:
                return ["support", "assistance"]
                
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    async def suggest_knowledge_base_improvements(self, search_queries: List[str], failed_searches: List[str]) -> List[Dict[str, Any]]:
        """Suggest improvements to knowledge base based on user queries"""
        try:
            if not self.claude_chat:
                await self.initialize_ai_models()
            
            prompt = f"""
            Analyze these search patterns and suggest knowledge base improvements for Big Mann Entertainment:
            
            Successful Queries: {', '.join(search_queries)}
            Failed/No Results Queries: {', '.join(failed_searches)}
            
            Suggest 5 new articles or improvements:
            
            For each suggestion:
            1. Article title
            2. Key content areas to cover
            3. Target audience (artists, agents, admins)
            4. Priority (high, medium, low)
            5. Estimated impact on support ticket reduction
            
            Focus on Big Mann Entertainment's core services:
            - Music distribution
            - Licensing and royalties
            - Platform integrations
            - Content management
            - DAO governance
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.claude_chat.send_message(user_message)
            
            import json
            try:
                suggestions = json.loads(response)
                return suggestions
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Error suggesting KB improvements: {str(e)}")
            return []
    
    async def analyze_chat_sentiment(self, message_content: str) -> Dict[str, Any]:
        """Analyze sentiment of chat messages to detect escalation needs"""
        try:
            if not self.openai_chat:
                await self.initialize_ai_models()
            
            prompt = f"""
            Analyze the sentiment and urgency of this customer message:
            
            Message: {message_content}
            
            Provide:
            1. Sentiment (positive, neutral, negative, frustrated, angry)
            2. Urgency level (low, medium, high, critical)
            3. Escalation recommended (true/false)
            4. Key emotional indicators
            5. Suggested response tone
            
            Format as JSON:
            {{
                "sentiment": "sentiment_value",
                "urgency": "urgency_level", 
                "escalation_recommended": false,
                "emotional_indicators": ["indicator1", "indicator2"],
                "suggested_tone": "professional_and_empathetic"
            }}
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.openai_chat.send_message(user_message)
            
            import json
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                return {
                    "sentiment": "neutral",
                    "urgency": "medium",
                    "escalation_recommended": False,
                    "emotional_indicators": [],
                    "suggested_tone": "professional"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "sentiment": "neutral",
                "urgency": "low",
                "escalation_recommended": False,
                "emotional_indicators": [],
                "suggested_tone": "professional"
            }

# Global instance
ai_support_service = AISupportService()