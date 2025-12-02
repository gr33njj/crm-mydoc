"""
Telegram Bot для CRM MyDoctor
Уведомления и быстрые команды для пользователей
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.config import settings
from src.database import SessionLocal
from src.models import User, Task, TaskStatus, TaskPriority
from datetime import datetime, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    telegram_id = update.effective_user.id
    db = get_db()
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if user:
            await update.message.reply_text(
                f"Привет, {user.full_name}! Вы уже зарегистрированы в CRM MyDoctor.\n\n"
                "Доступные команды:\n"
                "/tasks - Мои активные задачи\n"
                "/today - Задачи на сегодня\n"
                "/complete <ID> - Закрыть задачу\n"
                "/help - Справка"
            )
        else:
            await update.message.reply_text(
                "Добро пожаловать в CRM MyDoctor!\n\n"
                "Чтобы связать ваш Telegram с аккаунтом, введите ваш email:\n"
                "Формат: /register email@example.com"
            )
    finally:
        db.close()


async def register_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /register command"""
    telegram_id = update.effective_user.id
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Использование: /register email@example.com")
        return
    
    email = context.args[0].lower()
    db = get_db()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            await update.message.reply_text("Пользователь с таким email не найден в системе.")
            return
        
        if user.telegram_id:
            await update.message.reply_text("Этот аккаунт уже привязан к Telegram.")
            return
        
        user.telegram_id = telegram_id
        db.commit()
        
        await update.message.reply_text(
            f"✅ Успешно! Ваш Telegram привязан к аккаунту {user.full_name}.\n\n"
            "Теперь вы будете получать уведомления о задачах."
        )
    except Exception as e:
        logger.error(f"Error registering telegram: {e}")
        await update.message.reply_text("Произошла ошибка при регистрации.")
    finally:
        db.close()


async def get_my_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tasks command"""
    telegram_id = update.effective_user.id
    db = get_db()
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text("Вы не зарегистрированы. Используйте /start")
            return
        
        tasks = db.query(Task).filter(
            and_(
                Task.assignee_id == user.id,
                Task.status.in_([TaskStatus.NEW, TaskStatus.IN_PROGRESS])
            )
        ).order_by(Task.priority.desc(), Task.created_at).limit(10).all()
        
        if not tasks:
            await update.message.reply_text("✅ У вас нет активных задач!")
            return
        
        message = "📋 Ваши активные задачи:\n\n"
        
        for task in tasks:
            priority_emoji = {
                TaskPriority.CRITICAL: "🔴",
                TaskPriority.IMPORTANT: "🟡",
                TaskPriority.LOW: "🟢"
            }.get(task.priority, "⚪")
            
            deadline_str = ""
            if task.deadline:
                deadline_str = f"\n📅 Дедлайн: {task.deadline.strftime('%d.%m.%Y %H:%M')}"
            
            message += f"{priority_emoji} {task.title}\n"
            message += f"ID: {task.id}{deadline_str}\n"
            message += f"Статус: {task.status.value}\n\n"
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        await update.message.reply_text("Произошла ошибка при получении задач.")
    finally:
        db.close()


async def get_today_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command"""
    telegram_id = update.effective_user.id
    db = get_db()
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text("Вы не зарегистрированы. Используйте /start")
            return
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        tasks = db.query(Task).filter(
            and_(
                Task.assignee_id == user.id,
                Task.deadline >= today_start,
                Task.deadline < today_end,
                Task.status != TaskStatus.COMPLETED
            )
        ).order_by(Task.priority.desc()).all()
        
        if not tasks:
            await update.message.reply_text("📅 На сегодня задач с дедлайном нет!")
            return
        
        message = "📅 Задачи на сегодня:\n\n"
        
        for task in tasks:
            priority_emoji = {
                TaskPriority.CRITICAL: "🔴",
                TaskPriority.IMPORTANT: "🟡",
                TaskPriority.LOW: "🟢"
            }.get(task.priority, "⚪")
            
            message += f"{priority_emoji} {task.title}\n"
            message += f"ID: {task.id}\n"
            message += f"⏰ {task.deadline.strftime('%H:%M')}\n\n"
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting today tasks: {e}")
        await update.message.reply_text("Произошла ошибка.")
    finally:
        db.close()


async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /complete command"""
    telegram_id = update.effective_user.id
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Использование: /complete <task_id>")
        return
    
    task_id = context.args[0]
    db = get_db()
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            await update.message.reply_text("Вы не зарегистрированы. Используйте /start")
            return
        
        from uuid import UUID
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        
        if not task:
            await update.message.reply_text("❌ Задача не найдена.")
            return
        
        if task.assignee_id != user.id:
            await update.message.reply_text("❌ Эта задача назначена не вам.")
            return
        
        if task.status == TaskStatus.COMPLETED:
            await update.message.reply_text("✅ Задача уже выполнена.")
            return
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        db.commit()
        
        await update.message.reply_text(f"✅ Задача '{task.title}' выполнена!")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID задачи.")
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        await update.message.reply_text("Произошла ошибка.")
    finally:
        db.close()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
📚 Справка по командам CRM MyDoctor Bot:

/start - Начать работу с ботом
/register <email> - Привязать Telegram к аккаунту
/tasks - Показать мои активные задачи
/today - Задачи на сегодня
/complete <task_id> - Отметить задачу как выполненную
/help - Показать эту справку

📬 Вы будете получать уведомления о:
• Новых задачах
• Комментариях к вашим задачам
• Приближении дедлайнов
• Упоминаниях в чате
"""
    await update.message.reply_text(help_text)


async def send_notification_to_user(telegram_id: int, message: str) -> bool:
    """Send notification to specific user"""
    try:
        bot = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build().bot
        await bot.send_message(chat_id=telegram_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Error sending notification to {telegram_id}: {e}")
        return False


def main() -> None:
    """Start the bot"""
    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register_telegram))
    application.add_handler(CommandHandler("tasks", get_my_tasks))
    application.add_handler(CommandHandler("today", get_today_tasks))
    application.add_handler(CommandHandler("complete", complete_task))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start bot
    logger.info("Starting Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()







