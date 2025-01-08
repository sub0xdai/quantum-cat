import os
import re
import asyncio
from datetime import datetime
from typing import Dict, Optional
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from minimax_client import MinimaxClient
import logging
from rate_limiter import RateLimiter

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Constants
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    print("Error: TELEGRAM_TOKEN not found in .env file")
    print("Current working directory:", os.getcwd())
    print("Looking for .env in:", os.path.join(os.path.dirname(__file__), '.env'))

# Messages
GREETING_MESSAGE = """
✨ Welcome to QL Cat Bot! 🐱✨

On spectrum videos featuring our interdimensional slightly frazzled white Persian cat! 🎬

Use /help to see wassup 🌟
"""

HELP_MESSAGE = """
🎮 *Available Commands*

🎥 `/cat [action] [object]` - Generate a cat video
   Example: `/cat chase butterfly`

🔍 `/status [taskID]` - Check video status
   Example: `/status 224083523223649`

ℹ️ `/help` - Show this help message
🚀 `/start` - Start the bot
"""

PROCESSING_MESSAGE = "🎬 Your cat video is being generated!"
STATUS_MESSAGE = "🔄 Current status: *{status}*"
WAIT_MESSAGE = "⏳ This usually takes 3-5 minutes. The video will be sent here when it's ready."
TASK_ID_FORMAT = "🔑 Task ID: `{task_id}`"
RATE_LIMIT_MESSAGE = """⏳ Rate limit exceeded!
You can generate one video per hour.
Time remaining: {} minutes"""

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.minimax_client = MinimaxClient()
        
    def generate_task_id(self) -> str:
        """Generate a unique 22-digit task ID."""
        timestamp = int(datetime.now().timestamp() * 1000000)
        return str(timestamp).zfill(22)
    
    async def create_task(self, user_id: int, action: str, object_: str) -> str:
        """Create a new video generation task."""
        # Base cat description
        cat_desc = (
            "the iconic white Persian cat from the reference image - "
            "maintain its exact appearance: the fluffy pure white fur, round face, flat nose, "
            "grey eyes with that characteristic stern expression, and small ears hidden in the fluff"
        )
        
        # Camera and scene enhancements based on keywords
        camera_directions = {
            'eat': "Close-up shots of the cat's face, occasionally pulling back to show the full scene. Focus on the cat's expressions.",
            'chase': "Dynamic tracking shots following the cat's movement, mixing close-ups of the determined expression with wider shots of the action.",
            'sleep': "Gentle, slow panning shots. Occasional close-ups of the peaceful sleeping face.",
            'play': "Mix of tracking shots and dynamic angles, capturing both the playful action and the cat's expressions.",
            'walk': "Smooth tracking shots from various angles, showing both the cat's movement and the environment.",
            'sit': "Steady shots that slowly circle around the cat, with occasional close-ups of its regal expression.",
            'jump': "Dynamic upward tracking shots, following the cat's graceful movement through the air.",
            'run': "Fast-paced tracking shots with dramatic angles, capturing the speed and energy.",
            'dance': "Smooth, circular camera movements that follow the rhythm, mixing wide and close-up shots.",
            'explore': "Following shots that reveal the environment as the cat discovers it.",
        }
        
        # Check for keywords in both action and object
        full_prompt = f"{action} {object_}".lower()
        matching_directions = []
        
        # Find all matching keywords
        for keyword, direction in camera_directions.items():
            if keyword in full_prompt:
                matching_directions.append(direction)
        
        # If no keywords match, use default
        if not matching_directions:
            camera_desc = "Mix of close-ups and wider shots, focusing on both the cat's expressions and the overall scene."
        else:
            # Combine matching directions, but don't make it too long
            camera_desc = " ".join(matching_directions[:2])  # Limit to 2 matching directions
        
        # Build cinematic prompt
        prompt = (
            f"Create a cinematic video featuring {cat_desc}. "
            f"\nScene: The Persian cat is {action} {object_}. "
            f"\nCinematography: {camera_desc} "
            "\nMaintain consistent lighting and ensure the cat's appearance matches the reference image exactly. "
            "The cat should look like it was taken directly from the reference and placed into this new scene. "
            "Create an appropriate, atmospheric environment that enhances the mood of the action."
        )
        
        # Submit task to Minimax
        task_id = await self.minimax_client.generate_video(prompt)
        
        self.tasks[task_id] = {
            'user_id': user_id,
            'action': action,
            'object': object_,
            'status': 'Processing',
            'timestamp': datetime.now().strftime('%H:%M'),
            'prompt': prompt
        }
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task."""
        if task_id not in self.tasks:
            return None
            
        status, file_id = await self.minimax_client.check_generation_status(task_id)
        self.tasks[task_id]['status'] = status
        
        if status == 'Success' and file_id:
            self.tasks[task_id]['file_id'] = file_id
            
        return status

    async def get_video_url(self, task_id: str) -> Optional[str]:
        """Get the video URL for a completed task."""
        if task_id not in self.tasks or 'file_id' not in self.tasks[task_id]:
            return None
            
        return await self.minimax_client.get_video_url(self.tasks[task_id]['file_id'])

class BotState:
    def __init__(self):
        self.is_running = False
        self.task_manager = TaskManager()

# Initialize global managers
task_manager = TaskManager()
rate_limiter = RateLimiter()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(GREETING_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(HELP_MESSAGE)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is an admin in the current chat."""
    if not update.effective_chat:
        return False
    
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id
        )
        return chat_member.status in ['administrator', 'creator']
    except Exception:
        return False

async def cat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cat command."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Please provide an action and object.\nExample: `/cat chase butterfly`",
            parse_mode='Markdown'
        )
        return

    # Check if user is admin
    admin_status = await is_admin(update, context)

    # Check rate limit
    user_id = update.effective_user.id
    allowed, seconds_remaining = rate_limiter.check_rate_limit(user_id, is_admin=admin_status)
    
    if not allowed:
        minutes_remaining = int(seconds_remaining / 60)
        await update.message.reply_text(
            RATE_LIMIT_MESSAGE.format(minutes_remaining),
            parse_mode='Markdown'
        )
        return

    action = context.args[0]
    object_ = ' '.join(context.args[1:])
    
    try:
        task_id = await task_manager.create_task(update.effective_user.id, action, object_)
        
        response = f"{PROCESSING_MESSAGE}\n"
        response += f"{STATUS_MESSAGE.format(status='Processing')}\n"
        response += f"{WAIT_MESSAGE}\n"
        response += f"{TASK_ID_FORMAT.format(task_id=task_id)}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Start monitoring the task
        asyncio.create_task(monitor_task(update, task_id))
    except Exception as e:
        error_message = f"Sorry, there was an error generating your video: {str(e)}"
        await update.message.reply_text(error_message)
        print(f"Error in cat_command: {str(e)}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    if not context.args:
        await update.message.reply_text("ℹ️ Please provide a task ID.\nExample: `/status 224083523223649`", parse_mode='Markdown')
        return
        
    task_id = context.args[0]
    status = await task_manager.get_task_status(task_id)
    
    if status:
        await update.message.reply_text(
            f"🎬 *Status for Task {task_id}*\n\n"
            f"🔄 Status: *{status}*",
            parse_mode='Markdown'
        )
        
        if status == 'Success':
            video_url = await task_manager.get_video_url(task_id)
            if video_url:
                # Download and send the video
                with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
                    if await task_manager.minimax_client.download_video(video_url, temp_file.name):
                        await update.message.reply_text("✨ Here's your video!")
                        await update.message.reply_video(video=open(temp_file.name, 'rb'))
    else:
        await update.message.reply_text("❌ Task not found. Please check your task ID.")

async def monitor_task(update: Update, task_id: str) -> None:
    """Monitor a video generation task and send updates."""
    max_retries = 3
    retry_count = 0
    
    while True:
        try:
            status = await task_manager.get_task_status(task_id)
            
            if status == 'Success':
                video_url = await task_manager.get_video_url(task_id)
                if video_url:
                    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
                        if await task_manager.minimax_client.download_video(video_url, temp_file.name):
                            await update.message.reply_text("✨ Your magical cat video is ready! 🎬")
                            await update.message.reply_video(video=open(temp_file.name, 'rb'))
                break
            elif status == 'Fail':
                await update.message.reply_text("❌ Sorry, something went wrong while creating your video. Please try again!")
                break
            elif status in ['Processing', 'Preparing', 'Queueing']:
                await asyncio.sleep(10)  # Check every 10 seconds
            else:
                print(f"Unexpected status received: {status}")
                retry_count += 1
                if retry_count >= max_retries:
                    await update.message.reply_text(f"⚠️ Unexpected status ({status}). Please try again or check later.")
                    break
                await asyncio.sleep(10)
        except Exception as e:
            print(f"Error in monitor_task: {str(e)}")
            retry_count += 1
            if retry_count >= max_retries:
                await update.message.reply_text("❌ Sorry, there was an error monitoring your video generation. Please try again.")
                break
            await asyncio.sleep(10)

def main():
    """Entry point for the bot."""
    try:
        # Create and run application
        app = (
            Application.builder()
            .token(TELEGRAM_TOKEN)
            .build()
        )
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("cat", cat_command))
        app.add_handler(CommandHandler("status", status_command))
        
        # Start the bot
        print("Starting bot...")
        app.run_polling()
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == '__main__':
    main()
