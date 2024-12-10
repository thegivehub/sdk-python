"""
GiveHub Python SDK
Version: 1.0.2
"""

import json
import requests
import websockets
import asyncio
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class GiveHubException(Exception):
    """Base exception for GiveHub SDK"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)

class StatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class GiveHubConfig:
    base_url: str = "https://api.thegivehub.com"
    version: str = "v1"
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class GiveHubSDK:
    def __init__(self, config: Union[Dict, GiveHubConfig]):
        if isinstance(config, dict):
            self.config = GiveHubConfig(**config)
        else:
            self.config = config
            
        self.session = requests.Session()
        self._init_modules()

    def _init_modules(self):
        """Initialize SDK modules"""
        self.auth = AuthModule(self)
        self.campaigns = CampaignModule(self)
        self.donations = DonationModule(self)
        self.impact = ImpactModule(self)
        self.updates = UpdateModule(self)
        self.notifications = NotificationModule(self)

    async def request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """Make an authenticated API request"""
        url = f"{self.config.base_url}/{self.config.version}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.config.api_key
        }

        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            if response.status_code == 401 and self.config.refresh_token:
                # Token expired, refresh and retry
                await self.auth.refresh_access_token()
                return await self.request(endpoint, method, **kwargs)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise GiveHubException(str(e), getattr(e.response, 'status_code', None))

class AuthModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk

    async def login(self, email: str, password: str) -> Dict:
        """Authenticate user and get access tokens"""
        response = await self.sdk.request(
            "/auth/login",
            method="POST",
            json={"email": email, "password": password}
        )

        if response.get("success"):
            self.sdk.config.access_token = response["tokens"]["accessToken"]
            self.sdk.config.refresh_token = response["tokens"]["refreshToken"]

        return response

    async def register(self, user_data: Dict) -> Dict:
        """Register a new user"""
        return await self.sdk.request(
            "/auth/register",
            method="POST",
            json=user_data
        )

    async def verify_email(self, email: str, code: str) -> Dict:
        """Verify user's email address"""
        return await self.sdk.request(
            "/auth/verify",
            method="POST",
            json={"email": email, "code": code}
        )

    async def refresh_access_token(self) -> Dict:
        """Refresh the access token using refresh token"""
        response = await self.sdk.request(
            "/auth/refresh",
            method="POST",
            json={"refreshToken": self.sdk.config.refresh_token}
        )

        if response.get("success"):
            self.sdk.config.access_token = response["accessToken"]

        return response

class CampaignModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk

    async def create(self, campaign_data: Dict) -> Dict:
        """Create a new campaign"""
        return await self.sdk.request(
            "/campaigns",
            method="POST",
            json=campaign_data
        )

    async def get(self, campaign_id: str) -> Dict:
        """Get campaign details"""
        return await self.sdk.request(f"/campaigns/{campaign_id}")

    async def list(self, **params) -> Dict:
        """List campaigns with optional filters"""
        return await self.sdk.request("/campaigns", params=params)

    async def update(self, campaign_id: str, update_data: Dict) -> Dict:
        """Update campaign details"""
        return await self.sdk.request(
            f"/campaigns/{campaign_id}",
            method="PUT",
            json=update_data
        )

    async def upload_media(self, campaign_id: str, file_path: str) -> Dict:
        """Upload media for a campaign"""
        with open(file_path, 'rb') as f:
            files = {'media': f}
            return await self.sdk.request(
                f"/campaigns/{campaign_id}/media",
                method="POST",
                files=files
            )

class DonationModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk

    async def create(self, donation_data: Dict) -> Dict:
        """Create a new donation"""
        return await self.sdk.request(
            "/donations",
            method="POST",
            json=donation_data
        )

    async def get_donations(self, **params) -> Dict:
        """Get donations with optional filters"""
        return await self.sdk.request("/donations", params=params)

    async def create_recurring(self, donation_data: Dict) -> Dict:
        """Set up a recurring donation"""
        return await self.sdk.request(
            "/donations/recurring",
            method="POST",
            json=donation_data
        )

    async def cancel_recurring(self, subscription_id: str) -> Dict:
        """Cancel a recurring donation"""
        return await self.sdk.request(
            f"/donations/recurring/{subscription_id}",
            method="DELETE"
        )

class ImpactModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk

    async def create_metrics(self, campaign_id: str, metrics_data: Dict) -> Dict:
        """Create impact metrics for a campaign"""
        data = {"campaignId": campaign_id, **metrics_data}
        return await self.sdk.request(
            "/impact/metrics",
            method="POST",
            json=data
        )

    async def update_metrics(self, metric_id: str, update_data: Dict) -> Dict:
        """Update impact metrics"""
        return await self.sdk.request(
            f"/impact/metrics/{metric_id}",
            method="PUT",
            json=update_data
        )

    async def get_metrics(self, campaign_id: str, **params) -> Dict:
        """Get impact metrics for a campaign"""
        return await self.sdk.request(
            f"/impact/metrics/{campaign_id}",
            params=params
        )

class UpdateModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk

    async def create(self, update_data: Dict) -> Dict:
        """Create a campaign update"""
        return await self.sdk.request(
            "/updates",
            method="POST",
            json=update_data
        )

    async def get_updates(self, **params) -> Dict:
        """Get campaign updates"""
        return await self.sdk.request("/updates", params=params)

    async def upload_media(self, update_id: str, file_path: str) -> Dict:
        """Upload media for an update"""
        with open(file_path, 'rb') as f:
            files = {'media': f}
            return await self.sdk.request(
                f"/updates/{update_id}/media",
                method="POST",
                files=files
            )

class NotificationModule:
    def __init__(self, sdk: GiveHubSDK):
        self.sdk = sdk
        self.websocket = None
        self.listeners = {}

    async def get_notifications(self, **params) -> Dict:
        """Get notifications"""
        return await self.sdk.request("/notifications", params=params)

    async def connect(self):
        """Connect to real-time notifications"""
        if not self.sdk.config.access_token:
            raise GiveHubException("Authentication required for notifications")

        ws_url = self.sdk.config.base_url.replace('http', 'ws')
        self.websocket = await websockets.connect(
            f"{ws_url}/notifications"
        )

        # Send authentication
        await self.websocket.send(json.dumps({
            "type": "auth",
            "token": self.sdk.config.access_token
        }))

        # Start listening for messages
        asyncio.create_task(self._listen())

    async def _listen(self):
        """Listen for websocket messages"""
        try:
            while True:
                message = await self.websocket.recv()
                notification = json.loads(message)
                
                if notification["type"] in self.listeners:
                    for callback in self.listeners[notification["type"]]:
                        await callback(notification)
        except websockets.exceptions.ConnectionClosed:
            # Handle reconnection
            await self.connect()

    def on(self, event_type: str, callback):
        """Register event listener"""
        if event_type not in self.listeners:
            self.listeners[event_type] = set()
        self.listeners[event_type].add(callback)

    def off(self, event_type: str, callback):
        """Remove event listener"""
        if event_type in self.listeners:
            self.listeners[event_type].discard(callback)

    async def disconnect(self):
        """Disconnect from notifications"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
