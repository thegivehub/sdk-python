import asyncio
from givehub import GiveHubSDK, GiveHubException

async def main():
    # Initialize SDK
    givehub = GiveHubSDK({
        'base_url': 'https://api.thegivehub.com',
        'version': 'v1',
        'api_key': 'your-api-key'
    })

    # Authentication Examples
    try:
        # Login
        login_result = await givehub.auth.login('user@example.com', 'password123')
        print(f"Logged in as: {login_result['user']['username']}")

        # Register new user
        user_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'firstName': 'John',
            'lastName': 'Doe'
        }
        await givehub.auth.register(user_data)
    except GiveHubException as e:
        print(f"Auth error: {str(e)}")

    # Campaign Examples
    try:
        # Create campaign
        campaign = await givehub.campaigns.create({
            'title': 'Clean Water Project',
            'description': 'Providing clean water access to remote communities',
            'targetAmount': 50000,
            'category': 'water',
            'milestones': [{
                'description': 'Phase 1: Survey',
                'amount': 10000
            }]
        })

        # Upload campaign media
        await givehub.campaigns.upload_media(
            campaign['id'],
            '/path/to/campaign-photo.jpg'
        )

        # Get campaign list
        campaigns = await givehub.campaigns.list(
            category='water',
            status='active',
            page=1,
            limit=10
        )
    except GiveHubException as e:
        print(f"Campaign error: {str(e)}")

    # Donation Examples
    try:
        # Create one-time donation
        donation = await givehub.donations.create({
            'campaignId': 'campaign-id',
            'amount': {
                'value': 100,
                'currency': 'USD'
            },
            'type': 'one-time'
        })

        # Create recurring donation
        recurring = await givehub.donations.create_recurring({
            'campaignId': 'campaign-id',
            'amount': {
                'value': 50,
                'currency': 'USD'
            },
            'frequency': 'monthly'
        })

        # Get donations
        donations = await givehub.donations.get_donations(
            campaignId='campaign-id',
            status='completed'
        )
    except GiveHubException as e:
        print(f"Donation error: {str(e)}")

    # Impact Tracking Examples
    try:
        # Create impact metrics
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

        # Get impact metrics
        impact = await givehub.impact.get_metrics('campaign-id',
            from_date='2024-01-01',
            to_date='2024-12-31'
        )
    except GiveHubException as e:
        print(f"Impact error: {str(e)}")

    # Update Examples
    try:
        # Create campaign update
        update = await givehub.updates.create({
            'campaignId': 'campaign-id',
            'title': 'Construction Progress',
            'content': 'We have completed the first phase of well construction.',
            'type': 'milestone'
        })

        # Upload update media
        await givehub.updates.upload_media(
            update['id'],
            '/path/to/progress-photo.jpg'
        )
    except GiveHubException as e:
        print(f"Update error: {str(e)}")

    # Notification Examples
    async def handle_donation(notification):
        print(f"New donation received: {notification['amount']}")
        # Update UI or trigger other actions

    async def handle_milestone(notification):
        print(f"Milestone completed: {notification['milestone']['description']}")
        # Update campaign progress

    try:
        # Connect to notifications
        await givehub.notifications.connect()

        # Register notification handlers
        givehub.notifications.on('donation_received', handle_donation)
        givehub.notifications.on('milestone_completed', handle_milestone)

        # Keep connection alive
        await asyncio.sleep(3600)  # 1 hour
    except GiveHubException as e:
        print(f"Notification error: {str(e)}")
    finally:
        await givehub.notifications.disconnect()

# Run the example
if __name__ == "__main__":
    asyncio.run(main())

# More Complex Examples

class CampaignManager:
    def __init__(self, givehub: GiveHubSDK):
        self.givehub = givehub

