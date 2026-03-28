"""
Utilities Module for Telegram Moderation Bot

This module provides utility functions for the bot including:
- Logging configuration and setup
- Moderation action logging and tracking
- Log formatting and display

All moderation actions are logged here for audit trail and transparency.

Author: Divyansh Shakya
"""

import logging
import time
import sys
from collections import defaultdict

def setup_logging():
    """
    Configure logging for the bot.
    
    Sets up both file and console logging with proper formatting and encoding.
    Logs are written to 'bot.log' file and displayed in console.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create formatter for log files
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create formatter for console (handle encoding)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler - writes logs to bot.log with UTF-8 encoding
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    
    # Console handler - displays logs in terminal with proper encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger with INFO level
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

moderation_log = []

def log_moderation_action(admin_id, admin_name, action, target_id, target_name, chat_id, success=True):
    """
    Log all moderation actions for audit trail.
    
    Records every moderation action (ban, mute, kick, etc.) with details
    including who performed it, on whom, and whether it succeeded.
    
    Args:
        admin_id (int): ID of admin who performed the action
        admin_name (str): Username or name of the admin
        action (str): Type of action (banned, muted, kicked, etc.)
        target_id (int): ID of user who was moderated
        target_name (str): Username or name of target user
        chat_id (int): Group/chat where action was performed
        success (bool): Whether the action succeeded (default: True)
    """
    log_entry = {
        'timestamp': time.time(),
        'admin_id': admin_id,
        'admin_name': admin_name,
        'action': action,
        'target_id': target_id,
        'target_name': target_name,
        'chat_id': chat_id,
        'success': success
    }
    moderation_log.append(log_entry)
    status = 'SUCCESS' if success else 'FAILED'
    logger.info(f"MODERATION: {admin_name} ({admin_id}) {action} {target_name} ({target_id}) in {chat_id} - {status}")

def get_recent_logs(count=5):
    """
    Get recent moderation logs.
    
    Retrieves the most recent moderation actions from memory.
    Used by the /logs command to display recent activity.
    
    Args:
        count (int): Number of recent logs to retrieve (default: 5)
        
    Returns:
        list: List of recent log entries (dictionaries)
    """
    return moderation_log[-count:] if moderation_log else []

def format_log_text(logs):
    """
    Format logs for display in Telegram.
    
    Converts log entries into a formatted string suitable for
    sending as a message in Telegram.
    
    Args:
        logs (list): List of log entry dictionaries
        
    Returns:
        str: Formatted log text with emojis and timestamps
    """
    if not logs:
        return "📋 No moderation actions logged yet."
    
    log_text = "📋 **Recent Moderation Actions:**\n\n"
    for log in logs:
        timestamp = time.strftime('%H:%M:%S', time.localtime(log['timestamp']))
        status = "✅" if log['success'] else "❌"
        log_text += f"{status} `{timestamp}` - {log['admin_name']} {log['action']} {log['target_name']}\n"
    
    return log_text
