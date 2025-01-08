# QL Cat Bot Instructions

## Core Bot Behavior

1. Initial Greeting
   - When `/start` is used, bot responds with: "👋 Hello! I'm QL Cat Bot! Use `/help` to see available commands."
   - Greeting should include the waving hand emoji and maintain friendly tone

2. Command Structure
   ```
   /start - Initiates bot interaction
   /help - Shows available commands
   /cat [action] [object] - Generates cat video with specified action and object
   /status [taskID] - Checks status of video generation task
   ```

3. Video Generation Process
   - When receiving a cat action command (e.g., `/cat eat some noodles`):
     1. Respond immediately with "Your cat video is being generated!"
     2. Follow with status: "Current status: Processing"
     3. Include notice: "This usually takes 3-5 minutes. The video will be sent here when it's ready."
     4. Provide Task ID in format: "Task ID: [22-digit number]"

4. Status Checking
   - Accept status checks in format: `/status [22-digit taskID]`
   - Verify task ID matches format: 22 digits (example: 224080850202733)
   - Return current generation status

5. Response Formatting
   - All timestamps should be shown in HH:mm format
   - Command messages should be shown in purple/violet bubbles
   - Bot responses should be in dark mode compatible format
   - Task IDs should be readily copyable

## Implementation Details

1. Command Processing
```python
async def process_cat_command(message: str) -> Dict:
    """
    Process cat action commands
    Format: /cat [action] [object]
    
    Returns:
        Dict containing:
        - task_id: str (22 digits)
        - status: str
        - timestamp: str (HH:mm)
    """
    pass

async def check_status(task_id: str) -> str:
    """
    Check status of video generation
    Format: /status [22-digit task_id]
    
    Returns:
        Current status of the task
    """
    pass
```

2. Video Generation Status States
   - Processing: Initial state when task begins
   - Rendering: Video is being rendered
   - Downloading: Video is being prepared for delivery
   - Complete: Video is ready to send
   - Failed: Generation encountered an error

3. Error Handling
   - Invalid commands should prompt user to use `/help`
   - Invalid task IDs should return clear error message
   - Network/API failures should notify user of retry status

## Configuration

```dotenv
# Bot Configuration
TELEGRAM_TOKEN=your_telegram_token
MINIMAX_API_KEY=your_minimax_api_key

# Video Generation
MAX_VIDEO_DURATION=300
GENERATION_TIMEOUT=600
RETRY_ATTEMPTS=3

# Response Templates
GREETING_MESSAGE=👋 Hello! I'm QL Cat Bot! Use /help to see available commands.
PROCESSING_MESSAGE=Your cat video is being generated!
STATUS_MESSAGE=Current status: {status}
WAIT_MESSAGE=This usually takes 3-5 minutes. The video will be sent here when it's ready.
TASK_ID_FORMAT=Task ID: {task_id}
```

## Security and Rate Limiting

1. Command Limits
   - Maximum 5 pending generations per user
   - Cooldown period between commands: 60 seconds
   - Maximum video length: 5 minutes

2. Task ID Validation
   - Must be exactly 22 digits
   - Should only contain numbers
   - Should match existing task in database

## Deployment Requirements

1. System Requirements
   - Python 3.13+
   - Telegram Bot API
   - Minimax.ai API access
   - PostgreSQL for task tracking

2. Monitoring
   - Log all command attempts
   - Track generation success rate
   - Monitor API response times

## Testing Scenarios

1. Command Testing
   ```python
   # Test cases
   /cat eat some noodles  # Should generate task ID
   /status 224080850202733  # Should return status
   /cat sleep on bed  # Should generate different task ID
   ```

2. Error Cases
   ```python
   /cat  # Should prompt for action
   /status invalid  # Should return error
   /unknown  # Should suggest /help
   ```