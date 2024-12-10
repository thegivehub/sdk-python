# The Give Hub Python SDK Documentation

## Installation

### Requirements
- Python 3.8 or higher
- aiohttp
- websockets

### Via pip
```bash
pip install givehub-sdk
```

### Via poetry
```bash
poetry add givehub-sdk
```

## Quick Start

```python
import asyncio
from givehub import GiveHubSDK

async def main():
    # Initialize the SDK
    givehub = GiveHubSDK({
        'base_url': 'https://api.thegivehub.com',
        'version': 'v1',
        'api_key': 'your-api-key'
    })
    
    # Use the SDK
    try:
        campaigns = await givehub.campaigns.list()
        print('Active campaigns:', campaigns)
    except GiveHubException as e:
        print('Error:', str(e))

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

### Login
```python
try:
    result = await givehub.auth.login('user@example.com', 'password123')
    print(f"Logged in as: {result['user']['username']}")
except GiveHubException as e:
    print(f"Login failed: {str(e)}")
```

### Register
```python
try:
    user_data = {
        'email': 'newuser@example.com',
        'password': 'secure123',
        'firstName': 'John',
        'lastName': 'Doe'
    }
    result = await givehub.auth.register(user_data)
    print(f"Registration successful. User ID: {result['userId']}")
except GiveHubException as e:
    print(f"Registration failed: {str(e)}")
```

### Verify Email
```python
try:
    await givehub.auth.verify_email('user@example.com', '123456')
    print("Email verified successfully")
except GiveHubException as e:
    print(f"Verification failed: {str(e)}")
```

## Campaign Management

### Create Campaign
```python
try:
    campaign = await givehub.campaigns.create({
        'title': 'Clean Water Project',
        'description': 'Providing clean water access',
        'targetAmount': 50000,
        'category': 'water',
        'milestones': [{
            'description': 'Phase 1: Survey',
            'amount': 10000
        }]
    })
    print(f"Campaign created with ID: {campaign['id']}")
except GiveHubException as e:
    print(f"Failed to create campaign: {str(e)}")
```

### Get Campaign Details
```python
try:
    campaign = await givehub.campaigns.get('campaign-id')
    print(f"Campaign title: {campaign['title']}")
except GiveHubException as e:
    print(f"Failed to get campaign: {str(e)}")
```

### List Campaigns
```python
try:
    campaigns = await givehub.campaigns.list(
        category='water',
        status='active',
        page=1,
        limit=10
    )
    for campaign in campaigns['data']:
        print(campaign['title'])
except GiveHubException as e:
    print(f"Failed to list campaigns: {str(e)}")
```

### Upload Campaign Media
```python
try:
    result = await givehub.campaigns.upload_media(
        'campaign-id',
        '/path/to/image.jpg'
    )
    print("Media uploaded successfully")
except GiveHubException as e:
    print(f"Upload failed: {str(e)}")
```

## Donations

### Process Donation
```python
try:
    donation = await givehub.donations.create({
        'campaignId': 'campaign-id',
        'amount': {
            'value': 100,
            'currency': 'USD'
        },
        'type': 'one-time'
    })
    print("Donation processed successfully")
except GiveHubException as e:
    print(f"Donation failed: {str(e)}")
```

### Create Recurring Donation
```python
try:
    recurring = await givehub.donations.create_recurring({
        'campaignId': 'campaign-id',
        'amount': {
            'value': 50,
            'currency': 'USD'
        },
        'frequency': 'monthly'
    })
    print("Recurring donation set up successfully")
except GiveHubException as e:
    print(f"Failed to set up recurring donation: {str(e)}")
```

## Impact Tracking

### Create Impact Metrics
```python
try:
    metrics = await givehub.impact.create_metrics('campaign-id', {
        'metrics': [{
            'name': 'People Helped',
            'value': 500,
            'unit': 'individuals'
        }, {
            'name': 'Water Access',
            'value': 1000,
            'unit': 'liters/day'
        }]
    })
    print("Impact metrics created successfully")
except GiveHubException as e:
    print(f"Failed to create metrics: {str(e)}")
```

## Real-time Notifications

### Using Async Context Manager
```python
async with givehub.notifications as notifications:
    # Register handlers
    @notifications.on('donation_received')
    async def handle_donation(notification):
        print(f"New donation: {notification['amount']}")

    @notifications.on('milestone_completed')
    async def handle_milestone(notification):
        print(f"Milestone completed: {notification['milestone']}")

    # Keep connection alive
    await asyncio.sleep(3600)  # 1 hour
```

### Manual Connection Management
```python
try:
    # Connect to notifications
    await givehub.notifications.connect()

    # Register handlers
    async def handle_donation(notification):
        print(f"New donation: {notification['amount']}")

    givehub.notifications.on('donation_received', handle_donation)

    # Keep connection alive
    await asyncio.sleep(3600)  # 1 hour

finally:
    # Clean up
    await givehub.notifications.disconnect()
```

## Advanced Usage Examples

### Campaign Manager Class
```python
class CampaignManager:
    def __init__(self, givehub: GiveHubSDK):
        self.givehub = givehub

    async def create_campaign_with_milestones(self, data: dict, milestones: list):
        try:
            # Create campaign
            campaign = await self.givehub.campaigns.create({
                'title': data['title'],
                'description': data['description'],
                'targetAmount': data['targetAmount'],
                'category': data['category'],
                'milestones': milestones
            })

            # Upload media if provided
            if 'mediaPath' in data:
                await self.givehub.campaigns.upload_media(
                    campaign['id'],
                    data['mediaPath']
                )

            return campaign

        except GiveHubException as e:
            logging.error(f"Campaign creation failed: {str(e)}")
            raise
```

### Impact Tracker Class
```python
class ImpactTracker:
    def __init__(self, givehub: GiveHubSDK):
        self.givehub = givehub

    async def track_progress(self, campaign_id: str, metrics: list):
        try:
            # Update metrics
            result = await self.givehub.impact.update_metrics(
                campaign_id,
                {'metrics': metrics}
            )

            # Create update
            await self._create_impact_update(campaign_id, metrics)

            return result

        except GiveHubException as e:
            logging.error(f"Impact tracking failed: {str(e)}")
            raise

    async def _create_impact_update(self, campaign_id: str, metrics: list):
        content = "Impact Update:\n\n"
        for metric in metrics:
            content += f"- {metric['name']}: {metric['value']} {metric['unit']}\n"

        return await self.givehub.updates.create({
            'campaignId': campaign_id,
            'title': 'Impact Metrics Updated',
            'content': content,
            'type': 'impact'
        })
```

## Type Hints

The SDK provides comprehensive type hints for better IDE support:

```python
from givehub.types import (
    Campaign,
    Donation,
    ImpactMetric,
    Update,
    Notification
)

async def process_campaign(campaign: Campaign) -> None:
    pass

async def handle_donation(donation: Donation) -> None:
    pass
```

## Error Handling

The SDK raises `GiveHubException` for all errors:

```python
try:
    result = await givehub.campaigns.create(campaign_data)
except GiveHubException as e:
    if e.status_code == 401:
        # Handle authentication error
        pass
    elif e.status_code == 400:
        # Handle validation error
        pass
    else:
        # Handle other errors
        pass
    
    logging.error(f"API Error: {str(e)}")
```

## Configuration Options

```python
config = {
    'base_url': 'https://api.thegivehub.com',  # API base URL
    'version': 'v1',                           # API version
    'api_key': 'your-api-key',                # Your API key
    'timeout': 30,                            # Request timeout in seconds
    'verify_ssl': True,                       # Verify SSL certificates
    'debug': False                            # Enable debug mode
}
```

## Best Practices

1. Use async context managers for resource management
2. Implement proper error handling and logging
3. Store configuration in environment variables
4. Validate data before making API calls
5. Use type hints for better code maintainability

## Debugging

Enable debug mode to see detailed logs:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

givehub = GiveHubSDK({
    'debug': True,
    # other config...
})
```

## Support
- Documentation: https://docs.thegivehub.com
- GitHub Issues: https://github.com/thegivehub/sdk-python/issues
- Email: support@givehub.com
