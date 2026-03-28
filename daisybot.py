import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import telegram
from datetime import datetime, timedelta

# تفعيل السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توكن البوت (احصل عليه من BotFather)
TOKEN = 'bot_token'

user_data = {}

# تفاصيل مالك البوت
OWNER_ID = YOUR_USERID
OWNER_USERNAME = "@realcodedbyom"

def is_owner(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم هو مالك البوت."""
    return user_id == OWNER_ID

def is_admin(update: Update, context: CallbackContext) -> bool:
    """التحقق مما إذا كان المستخدم مشرفاً أو المالك."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if is_owner(user_id):
        return True
    
    try:
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"خطأ في التحقق من صلاحيات المشرف: {e}")
        return False

def bot_has_admin_rights(context: CallbackContext, chat_id: int) -> bool:
    """التحقق مما إذا كان البوت يمتلك صلاحيات مشرف."""
    try:
        bot_member = context.bot.get_chat_member(chat_id, context.bot.id)
        return bot_member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"خطأ في التحقق من صلاحيات البوت: {e}")
        return False

def start(update: Update, context: CallbackContext) -> None:
    """إرسال رسالة عند إصدار الأمر /start."""
    user = update.effective_user
    welcome_message = (
        f"🌼 أهلاً بك في بوت ديزي، {user.mention_markdown_v2()}\! 🌼\n\n"
        f"أنا هنا لمساعدتك في إدارة الدردشة وجعلها أكثر تنظيماً ومتعة\. 🌺\n\n"
        f"🔧 بواسطة: {OWNER_USERNAME}\n"
        f"🚀 الإصدار: 1\.0\n"
        f"💡 استخدم help لرؤية الأوامر المتاحة\n\n"
        f"لننتقل بالدردشة إلى مستوى آخر معاً\! 🌻"
    )
    update.message.reply_markdown_v2(welcome_message)
    main_menu(update, context)

def main_menu(update: Update, context: CallbackContext) -> None:
    """عرض القائمة الرئيسية."""
    keyboard = [
        [InlineKeyboardButton("👮 أوامر المشرفين", callback_data='admin_commands')],
        [InlineKeyboardButton("👥 أوامر المستخدمين", callback_data='user_commands')],
        [InlineKeyboardButton("🎉 أوامر التسلية", callback_data='fun_commands')],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('يرجى اختيار قسم:', reply_markup=reply_markup)
    else:
        query = update.callback_query
        query.answer()
        query.edit_message_text('يرجى اختيار قسم:', reply_markup=reply_markup)

def admin_commands(update: Update, context: CallbackContext) -> None:
    """عرض أوامر المشرفين."""
    keyboard = [
        [InlineKeyboardButton("🚫 حظر", callback_data='ban'),
         InlineKeyboardButton("✅ إلغاء حظر", callback_data='unban')],
        [InlineKeyboardButton("👢 طرد", callback_data='kick'),
         InlineKeyboardButton("🔇 كتم", callback_data='mute')],
        [InlineKeyboardButton("🔊 إلغاء كتم", callback_data='unmute'),
         InlineKeyboardButton("⚠️ تحذير", callback_data='warn')],
        [InlineKeyboardButton("🔄 إزالة تحذير", callback_data='unwarn'),
         InlineKeyboardButton("🎖️ رفع مشرف", callback_data='promote')],
        [InlineKeyboardButton("⬇️ تنزيل مشرف", callback_data='demote'),
         InlineKeyboardButton("🧹 تنظيف", callback_data='purge')],
        [InlineKeyboardButton("🔍 تصفية (فلتر)", callback_data='filter'),
         InlineKeyboardButton("🛑 إيقاف فلتر", callback_data='stop')],
        [InlineKeyboardButton("📋 قائمة الفلاتر", callback_data='filterlist'),
         InlineKeyboardButton("🌐🚫 حظر عام", callback_data='gban')],
        [InlineKeyboardButton("🔒 قفل الكل", callback_data='lockall'),
         InlineKeyboardButton("🔓 فتح الكل", callback_data='unlockall')],
        [InlineKeyboardButton("🗑️⚠️ حذف وتحذير", callback_data='dwarn'),
         InlineKeyboardButton("🗑️🔇 حذف وكتم", callback_data='dmute')],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    query.edit_message_text('أوامر المشرفين:', reply_markup=reply_markup)

def user_commands(update: Update, context: CallbackContext) -> None:
    """عرض أوامر المستخدمين."""
    keyboard = [
        [InlineKeyboardButton("ℹ️ معلومات", callback_data='info'),
         InlineKeyboardButton("🆔 الأيدي", callback_data='id')],
        [InlineKeyboardButton("📜 القوانين", callback_data='rules'),
         InlineKeyboardButton("❓ مساعدة", callback_data='help')],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    query.edit_message_text('أوامر المستخدمين:', reply_markup=reply_markup)

def fun_commands(update: Update, context: CallbackContext) -> None:
    """عرض أوامر التسلية."""
    keyboard = [
        [InlineKeyboardButton("🎲 رمي نرد", callback_data='roll_dice'),
         InlineKeyboardButton("🪙 عملة معدنية", callback_data='flip_coin')],
        [InlineKeyboardButton("🔢 رقم عشوائي", callback_data='random_number'),
         InlineKeyboardButton("💬 حكمة", callback_data='quote')],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    query.edit_message_text('أوامر التسلية:', reply_markup=reply_markup)

def settings(update: Update, context: CallbackContext) -> None:
    """عرض الإعدادات."""
    keyboard = [
        [InlineKeyboardButton("👋 رسالة الترحيب", callback_data='set_welcome'),
         InlineKeyboardButton("👋 رسالة الوداع", callback_data='set_goodbye')],
        [InlineKeyboardButton("📜 قوانين الدردشة", callback_data='set_rules'),
         InlineKeyboardButton("🛡️ مانع السبام", callback_data='set_antispam')],
        [InlineKeyboardButton("🌊 مانع التكرار", callback_data='set_antiflood')],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    query.edit_message_text('الإعدادات:', reply_markup=reply_markup)

def ban(update: Update, context: CallbackContext) -> None:
    """حظر مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا، لا يمكنني حظر الأعضاء.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.ban_chat_member(chat_id, user_id)
            update.message.reply_text(f"🚫 تم حظر المستخدم {user_id}.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل الحظر: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لحظره.")

def unban(update: Update, context: CallbackContext) -> None:
    """إلغاء حظر مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا.")
        return
    
    if context.args:
        user_id = int(context.args[0])
        try:
            context.bot.unban_chat_member(chat_id, user_id)
            update.message.reply_text(f"✅ تم إلغاء حظر المستخدم {user_id}.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل إلغاء الحظر: {str(e)}")
    else:
        update.message.reply_text("يرجى تزويد أيدي المستخدم لإلغاء حظره.")

def kick(update: Update, context: CallbackContext) -> None:
    """طرد مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.kick_chat_member(chat_id, user_id)
            context.bot.unban_chat_member(chat_id, user_id)
            update.message.reply_text(f"👢 تم طرد المستخدم {user_id}.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل الطرد: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لطرده.")

def mute(update: Update, context: CallbackContext) -> None:
    """كتم مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.restrict_chat_member(
                chat_id, 
                user_id, 
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
            )
            update.message.reply_text(f"🔇 تم كتم المستخدم {user_id}.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل الكتم: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لكتمه.")

def unmute(update: Update, context: CallbackContext) -> None:
    """إلغاء كتم مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.restrict_chat_member(
                chat_id, 
                user_id, 
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            update.message.reply_text(f"🔊 تم إلغاء كتم المستخدم {user_id}.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل إلغاء الكتم: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لإلغاء كتمه.")

def warn(update: Update, context: CallbackContext) -> None:
    """تحذير مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    if update.message.reply_to_message:
        warned_user = update.message.reply_to_message.from_user
        user_id = warned_user.id
        chat_id = update.effective_chat.id
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        if user_id not in user_data[chat_id]:
            user_data[chat_id][user_id] = {"warnings": 0}
        
        user_data[chat_id][user_id]["warnings"] += 1
        warn_count = user_data[chat_id][user_id]["warnings"]
        
        update.message.reply_text(f"⚠️ المستخدم {warned_user.mention_markdown_v2()} تلقى تحذيراً\. "
                                  f"عدد التحذيرات: {warn_count}", parse_mode='MarkdownV2')
        
        if warn_count >= 3:
            try:
                context.bot.kick_chat_member(chat_id, user_id)
                update.message.reply_text(f"🚫 تم حظر {warned_user.mention_markdown_v2()} بسبب تجاوز عدد التحذيرات المسموح بها\.", 
                                          parse_mode='MarkdownV2')
            except telegram.error.TelegramError as e:
                update.message.reply_text(f"❌ فشل الحظر: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لتحذيره.")

def unwarn(update: Update, context: CallbackContext) -> None:
    """إزالة تحذير من مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_id = user.id
        chat_id = update.effective_chat.id
        
        if chat_id in user_data and user_id in user_data[chat_id]:
            if user_data[chat_id][user_id]["warnings"] > 0:
                user_data[chat_id][user_id]["warnings"] -= 1
                warn_count = user_data[chat_id][user_id]["warnings"]
                update.message.reply_text(f"🔄 تم إزالة تحذير واحد من {user.mention_markdown_v2()}\. "
                                          f"عدد التحذيرات الحالي: {warn_count}", parse_mode='MarkdownV2')
            else:
                update.message.reply_text(f"المستخدم {user.mention_markdown_v2()} ليس لديه تحذيرات لإزالتها\.", parse_mode='MarkdownV2')
        else:
            update.message.reply_text(f"المستخدم {user.mention_markdown_v2()} ليس لديه تحذيرات\.", parse_mode='MarkdownV2')
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لإزالة التحذير.")

def promote(update: Update, context: CallbackContext) -> None:
    """ترقية مستخدم لمشرف."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أحتاج لصلاحيات مشرف لترقية الأعضاء.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        custom_title = ' '.join(context.args) if context.args else "مشرف"
        
        try:
            context.bot.promote_chat_member(chat_id, user_id,
                                            can_change_info=True,
                                            can_delete_messages=True,
                                            can_invite_users=True,
                                            can_restrict_members=True,
                                            can_pin_messages=True,
                                            can_promote_members=False)
            
            context.bot.set_chat_administrator_custom_title(chat_id, user_id, custom_title)
            
            update.message.reply_text(f"🎖️ تم رفع المستخدم {user_id} مشرفاً بلقب: {custom_title}")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل الترقية: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لترقيته.")

def demote(update: Update, context: CallbackContext) -> None:
    """تنزيل مشرف لرتبة مستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أحتاج لصلاحيات مشرف.")
        return
    
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.promote_chat_member(chat_id, user_id,
                                            can_change_info=False,
                                            can_delete_messages=False,
                                            can_invite_users=False,
                                            can_restrict_members=False,
                                            can_pin_messages=False,
                                            can_promote_members=False)
            update.message.reply_text(f"⬇️ تم تنزيل المستخدم {user_id} لرتبة مستخدم عادي.")
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ فشل التنزيل: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المشرف لتنزيله.")

def purge(update: Update, context: CallbackContext) -> None:
    """حذف عدد معين من الرسائل."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("يرجى تحديد عدد الرسائل المراد حذفها.")
        return
    
    try:
        num_messages = int(context.args[0])
    except ValueError:
        update.message.reply_text("يرجى إدخال رقم صحيح.")
        return
    
    if update.message.reply_to_message:
        message_id = update.message.reply_to_message.message_id
        deleted_count = 0
        
        for i in range(message_id, message_id + num_messages + 1):
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=i)
                deleted_count += 1
            except telegram.error.BadRequest:
                pass
        
        update.message.reply_text(f"🧹 تم تنظيف {deleted_count} رسالة.")
    else:
        update.message.reply_text("يرجى الرد على الرسالة التي تريد البدء بالحذف منها.")

def announcement(update: Update, context: CallbackContext) -> None:
    """إرسال إعلان لجميع المجموعات."""
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("🚫 هذا الأمر لمالك البوت فقط.")
        return
    
    message_reply = update.message.reply_to_message
    if message_reply:
        msj = message_reply.message_id
    elif context.args:
        msj = ' '.join(context.args)
    else:
        update.message.reply_text("يرجى تزويد نص الإعلان أو الرد على رسالة.")
        return

    chats = context.bot.get_updates()
    chat_ids = set(update.message.chat.id for update in chats if update.message)

    successful_sends = 0
    failed_sends = 0

    for chat_id in chat_ids:
        try:
            if message_reply:
                context.bot.forward_message(chat_id, update.effective_chat.id, msj)
            else:
                context.bot.send_message(chat_id, msj)
            successful_sends += 1
        except Exception as e:
            failed_sends += 1

    update.message.reply_text(f"تم إرسال الإعلان لـ {successful_sends} دردشة. فشل في {failed_sends}.")

def gban(update: Update, context: CallbackContext) -> None:
    """حظر عالمي للمستخدم."""
    if not is_owner(update.effective_user.id):
        update.message.reply_text("🚫 هذا الأمر لمالك البوت فقط.")
        return
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            chats = context.bot.get_updates()
            chat_ids = set(update.message.chat.id for update in chats if update.message)
            
            for chat_id in chat_ids:
                try:
                    context.bot.ban_chat_member(chat_id, user_id)
                except Exception:
                    continue
            
            update.message.reply_text(f"🌐🚫 تم حظر المستخدم {user_id} عالمياً من جميع الدردشات.")
        except Exception as e:
            update.message.reply_text(f"❌ فشل الحظر العالمي: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة المستخدم لحظره عالمياً.")

def filter_message(update: Update, context: CallbackContext) -> None:
    """حفظ رسالة كفلتر."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        if not context.args:
            update.message.reply_text("يرجى تزويد كلمة مفتاحية للفلتر.")
            return
        
        keyword = context.args[0].lower()
        message = update.message.reply_to_message
        
        if chat_id not in user_data:
            user_data[chat_id] = {}
        if "filters" not in user_data[chat_id]:
            user_data[chat_id]["filters"] = {}
        
        user_data[chat_id]["filters"][keyword] = {
            "text": message.text,
            "photo": message.photo[-1].file_id if message.photo else None,
            "document": message.document.file_id if message.document else None,
            "sticker": message.sticker.file_id if message.sticker else None,
            "animation": message.animation.file_id if message.animation else None,
            "video": message.video.file_id if message.video else None,
            "voice": message.voice.file_id if message.voice else None,
            "audio": message.audio.file_id if message.audio else None,
        }
        
        update.message.reply_text(f"تم حفظ الفلتر '{keyword}'.")
    else:
        update.message.reply_text("يرجى الرد على رسالة لحفظها كفلتر.")

def stop_filter(update: Update, context: CallbackContext) -> None:
    """إزالة فلتر."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("يرجى تحديد الكلمة المفتاحية للفلتر المراد حذفه.")
        return
    
    keyword = context.args[0].lower()
    
    if chat_id in user_data and "filters" in user_data[chat_id] and keyword in user_data[chat_id]["filters"]:
        del user_data[chat_id]["filters"][keyword]
        update.message.reply_text(f"تم إزالة الفلتر '{keyword}'.")
    else:
        update.message.reply_text(f"الفلتر '{keyword}' غير موجود.")

def filter_list(update: Update, context: CallbackContext) -> None:
    """عرض جميع الفلاتر النشطة."""
    chat_id = update.effective_chat.id
    
    if chat_id in user_data and "filters" in user_data[chat_id] and user_data[chat_id]["filters"]:
        f_list = "الفلاتر النشطة في هذه الدردشة:\n\n"
        for keyword in user_data[chat_id]["filters"].keys():
            f_list += f"- {keyword}\n"
        update.message.reply_text(f_list)
    else:
        update.message.reply_text("لا توجد فلاتر نشطة حالياً.")

def handle_filters(update: Update, context: CallbackContext) -> None:
    """التحقق من الرسائل الواردة للفلاتر."""
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower() if update.message.text else ""
    
    if chat_id in user_data and "filters" in user_data[chat_id]:
        for keyword, filter_data in user_data[chat_id]["filters"].items():
            if keyword in message_text:
                if filter_data["text"]:
                    update.message.reply_text(filter_data["text"])
                if filter_data["photo"]:
                    update.message.reply_photo(filter_data["photo"])
                if filter_data["document"]:
                    update.message.reply_document(filter_data["document"])
                if filter_data["sticker"]:
                    update.message.reply_sticker(filter_data["sticker"])
                if filter_data["animation"]:
                    update.message.reply_animation(filter_data["animation"])
                if filter_data["video"]:
                    update.message.reply_video(filter_data["video"])
                if filter_data["voice"]:
                    update.message.reply_voice(filter_data["voice"])
                if filter_data["audio"]:
                    update.message.reply_audio(filter_data["audio"])
                break

def lockall(update: Update, context: CallbackContext) -> None:
    """قفل جميع الصلاحيات."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أحتاج لصلاحيات مشرف.")
        return
    
    try:
        context.bot.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        update.message.reply_text("🔒 تم قفل جميع صلاحيات الدردشة.")
    except telegram.error.TelegramError as e:
        update.message.reply_text(f"❌ فشل القفل: {str(e)}")

def unlockall(update: Update, context: CallbackContext) -> None:
    """فتح جميع الصلاحيات."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا الأمر.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً هنا.")
        return
    
    try:
        context.bot.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        update.message.reply_text("🔓 تم فتح جميع صلاحيات الدردشة.")
    except telegram.error.TelegramError as e:
        update.message.reply_text(f"❌ فشل الفتح: {str(e)}")

def delete_and_warn(update: Update, context: CallbackContext) -> None:
    """حذف رسالة وتحذير المستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً.")
        return
    
    if update.message.reply_to_message:
        message_to_delete = update.message.reply_to_message
        user_to_warn = message_to_delete.from_user
        
        try:
            context.bot.delete_message(chat_id, message_to_delete.message_id)
            
            if chat_id not in user_data:
                user_data[chat_id] = {}
            if user_to_warn.id not in user_data[chat_id]:
                user_data[chat_id][user_to_warn.id] = {"warnings": 0}
            
            user_data[chat_id][user_to_warn.id]["warnings"] += 1
            warn_count = user_data[chat_id][user_to_warn.id]["warnings"]
            
            update.message.reply_text(f"🗑️⚠️ تم حذف الرسالة وتحذير {user_to_warn.mention_markdown_v2()}\. "
                                      f"عدد تحذيراته: {warn_count}", parse_mode='MarkdownV2')
            
            if warn_count >= 3:
                context.bot.kick_chat_member(chat_id, user_to_warn.id)
                update.message.reply_text(f"🚫 تم حظر {user_to_warn.mention_markdown_v2()} لتجاوز التحذيرات\.", parse_mode='MarkdownV2')
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة لحذفها وتحذير صاحبها.")

def delete_and_mute(update: Update, context: CallbackContext) -> None:
    """حذف رسالة وكتم المستخدم."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    
    chat_id = update.effective_chat.id
    
    if not bot_has_admin_rights(context, chat_id):
        update.message.reply_text("❌ أنا لست مشرفاً.")
        return
    
    if update.message.reply_to_message:
        message_to_delete = update.message.reply_to_message
        user_to_mute = message_to_delete.from_user
        
        try:
            context.bot.delete_message(chat_id, message_to_delete.message_id)
            context.bot.restrict_chat_member(
                chat_id, 
                user_to_mute.id, 
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
            )
            update.message.reply_text(f"🗑️🔇 تم حذف الرسالة وكتم {user_to_mute.mention_markdown_v2()}\.", 
                                      parse_mode='MarkdownV2')
        except telegram.error.TelegramError as e:
            update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    else:
        update.message.reply_text("يرجى الرد على رسالة لحذفها وكتم صاحبها.")

def info(update: Update, context: CallbackContext) -> None:
    """عرض معلومات المستخدم والدردشة."""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == 'private':
        info_text = f"👤 معلومات المستخدم:\n" \
                    f"الاسم: {user.full_name}\n" \
                    f"المعرف: @{user.username}\n" \
                    f"الأيدي: {user.id}\n"
    else:
        member_count = context.bot.get_chat_member_count(chat.id)
        info_text = f"👤 معلومات المستخدم:\n" \
                    f"الاسم: {user.full_name}\n" \
                    f"المعرف: @{user.username}\n" \
                    f"الأيدي: {user.id}\n\n" \
                    f"💬 معلومات الدردشة:\n" \
                    f"العنوان: {chat.title}\n" \
                    f"النوع: {chat.type}\n" \
                    f"أيدي الدردشة: {chat.id}\n" \
                    f"عدد الأعضاء: {member_count}\n"

    if chat.id in user_data and user.id in user_data[chat.id]:
        warnings = user_data[chat.id][user.id].get("warnings", 0)
        info_text += f"\nالتحذيرات: {warnings}"

    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(info_text, reply_markup=reply_markup)

def id_command(update: Update, context: CallbackContext) -> None:
    """عرض الأيديات بشكل سهل للنسخ."""
    user = update.effective_user
    chat = update.effective_chat

    id_text = f"أيدي المستخدم: `{user.id}`\n"
    if chat.type != 'private':
        id_text += f"أيدي الدردشة: `{chat.id}`"

    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(id_text, parse_mode='Markdown', reply_markup=reply_markup)

def rules(update: Update, context: CallbackContext) -> None:
    """عرض قوانين الدردشة."""
    chat_id = update.effective_chat.id

    if chat_id in user_data and "rules" in user_data[chat_id]:
        rules_text = f"📜 قوانين الدردشة:\n\n{user_data[chat_id]['rules']}"
    else:
        rules_text = "لم يتم وضع قوانين لهذه الدردشة بعد."

    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(rules_text, reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    """إرسال رسالة مساعدة."""
    help_text = "🌼 مساعدة بوت ديزي 🌼\n\n" \
                "إليك بعض الأوامر المتاحة:\n\n" \
                "start - تشغيل البوت\n" \
                "help - عرض رسالة المساعدة هذه\n" \
                "info - عرض معلومات المستخدم والدردشة\n" \
                "id - عرض الأيديات\n" \
                "rules - عرض قوانين الدردشة\n" \
                "ban - حظر مستخدم (للمشرفين)\n" \
                "unban - إلغاء حظر (للمشرفين)\n" \
                "kick - طرد مستخدم (للمشرفين)\n" \
                "mute - كتم مستخدم (للمشرفين)\n" \
                "unmute - إلغاء كتم (للمشرفين)\n" \
                "warn - تحذير مستخدم (للمشرفين)\n" \
                "unwarn - إزالة تحذير (للمشرفين)\n" \
                "roll_dice - رمي نرد\n" \
                "flip_coin - عملة معدنية\n" \
                "random_number - رقم عشوائي\n" \
                "quote - الحصول على حكمة عشوائية\n\n" \
                f"يتم إدارة البوت بواسطة: {OWNER_USERNAME}"

    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(help_text, reply_markup=reply_markup)

def roll_dice(update: Update, context: CallbackContext) -> None:
    """رمي نرد."""
    result = random.randint(1, 6)
    update.message.reply_text(f"🎲 لقد حصلت على الرقم {result}!")

def flip_coin(update: Update, context: CallbackContext) -> None:
    """رمي عملة معدنية."""
    result = random.choice(["ملك", "كتابة"])
    update.message.reply_text(f"🪙 النتيجة هي: {result}!")

def random_number(update: Update, context: CallbackContext) -> None:
    """توليد رقم عشوائي."""
    result = random.randint(1, 100)
    update.message.reply_text(f"🔢 رقمك العشوائي هو: {result}")

def quote(update: Update, context: CallbackContext) -> None:
    """إرسال حكمة عشوائية."""
    quotes = [
        "كن التغيير الذي تريد أن تراه في العالم. - غاندي",
        "ابق جائعاً، ابق أحمقاً. - ستيف جوبز",
        "الطريقة الوحيدة للقيام بعمل رائع هي أن تحب ما تفعله. - ستيف جوبز",
        "الحياة هي ما يحدث بينما أنت مشغول في وضع خطط أخرى. - جون لينون",
        "المستقبل ينتمي لأولئك الذين يؤمنون بجمال أحلامهم. - إليانور روزفلت"
    ]
    chosen_quote = random.choice(quotes)
    update.message.reply_text(f"📜 {chosen_quote}")

def set_welcome(update: Update, context: CallbackContext) -> None:
    """إعداد رسالة الترحيب."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("يرجى كتابة نص الترحيب.")
        return

    welcome_message = ' '.join(context.args)
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["welcome_message"] = welcome_message
    update.message.reply_text("👋 تم تعيين رسالة الترحيب بنجاح.")

def set_goodbye(update: Update, context: CallbackContext) -> None:
    """إعداد رسالة الوداع."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("يرجى كتابة نص الوداع.")
        return

    goodbye_message = ' '.join(context.args)
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["goodbye_message"] = goodbye_message
    update.message.reply_text("👋 تم تعيين رسالة الوداع بنجاح.")

def set_rules(update: Update, context: CallbackContext) -> None:
    """إعداد قوانين الدردشة."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("يرجى كتابة القوانين.")
        return

    rules_txt = ' '.join(context.args)
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["rules"] = rules_txt
    update.message.reply_text("📜 تم تعيين قوانين الدردشة بنجاح.")

def set_antispam(update: Update, context: CallbackContext) -> None:
    """إعداد مانع السبام."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    chat_id = update.effective_chat.id
    if not context.args or len(context.args) != 2:
        update.message.reply_text("يرجى تحديد عدد الرسائل والمدة الزمنية بالثواني.")
        return

    try:
        msg_limit = int(context.args[0])
        time_frame = int(context.args[1])
    except ValueError:
        update.message.reply_text("يرجى إدخال أرقام صحيحة.")
        return

    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["antispam"] = {"msg_limit": msg_limit, "time_frame": time_frame}
    update.message.reply_text(f"🛡️ تم تحديث إعدادات مانع السبام. "
                              f"سيتم تحذير من يرسل أكثر من {msg_limit} رسالة في {time_frame} ثانية.")

def set_antiflood(update: Update, context: CallbackContext) -> None:
    """إعداد مانع التكرار."""
    if not is_admin(update, context):
        update.message.reply_text("🚫 لا تملك صلاحية.")
        return
    chat_id = update.effective_chat.id
    if not context.args or len(context.args) != 2:
        update.message.reply_text("يرجى تحديد عدد الرسائل والمدة الزمنية بالثواني.")
        return

    try:
        msg_limit = int(context.args[0])
        time_frame = int(context.args[1])
    except ValueError:
        update.message.reply_text("يرجى إدخال أرقام صحيحة.")
        return

    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["antiflood"] = {"msg_limit": msg_limit, "time_frame": time_frame}
    update.message.reply_text(f"🌊 تم تحديث إعدادات مانع التكرار (Flood). "
                              f"سيتم كتم من يرسل أكثر من {msg_limit} رسالة في {time_frame} ثانية.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """معالجة الرسائل والتحقق من السبام والتكرار."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id in user_data:
        if "antispam" in user_data[chat_id]:
            antispam = user_data[chat_id]["antispam"]
            check_spam(update, context, antispam["msg_limit"], antispam["time_frame"])
        
        if "antiflood" in user_data[chat_id]:
            antiflood = user_data[chat_id]["antiflood"]
            check_flood(update, context, antiflood["msg_limit"], antiflood["time_frame"])
    
    handle_filters(update, context)

def check_spam(update: Update, context: CallbackContext, msg_limit: int, time_frame: int) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id not in user_data[chat_id]:
        user_data[chat_id][user_id] = {"messages": []}

    user_data[chat_id][user_id]["messages"].append(datetime.now())

    user_data[chat_id][user_id]["messages"] = [
        msg_time for msg_time in user_data[chat_id][user_id]["messages"]
        if (datetime.now() - msg_time).total_seconds() <= time_frame
    ]

    if len(user_data[chat_id][user_id]["messages"]) > msg_limit:
        warn(update, context)
        user_data[chat_id][user_id]["messages"] = []

def check_flood(update: Update, context: CallbackContext, msg_limit: int, time_frame: int) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id not in user_data[chat_id]:
        user_data[chat_id][user_id] = {"flood_messages": []}

    user_data[chat_id][user_id]["flood_messages"].append(datetime.now())

    user_data[chat_id][user_id]["flood_messages"] = [
        msg_time for msg_time in user_data[chat_id][user_id]["flood_messages"]
        if (datetime.now() - msg_time).total_seconds() <= time_frame
    ]

    if len(user_data[chat_id][user_id]["flood_messages"]) > msg_limit:
        mute(update, context)
        user_data[chat_id][user_id]["flood_messages"] = []

def button(update: Update, context: CallbackContext) -> None:
    """معالجة الضغط على الأزرار."""
    query = update.callback_query
    query.answer()

    if query.data == 'main_menu':
        main_menu(update, context)
    elif query.data == 'admin_commands':
        admin_commands(update, context)
    elif query.data == 'user_commands':
        user_commands(update, context)
    elif query.data == 'fun_commands':
        fun_commands(update, context)
    elif query.data == 'settings':
        settings(update, context)
    elif query.data in ['ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'unwarn', 'promote', 'demote', 'purge', 'filter', 'stop', 'filterlist', 'gban', 'lockall', 'unlockall', 'dwarn', 'dmute']:
        query.edit_message_text(f"استخدم الأمر {query.data} للقيام بـ {query.data.replace('_', ' ')}.")
    elif query.data in ['info', 'id', 'rules', 'help']:
        query.edit_message_text(f"استخدم الأمر {query.data} للحصول على {query.data.replace('_', ' ')}.")
    elif query.data in ['roll_dice', 'flip_coin', 'random_number', 'quote']:
        query.edit_message_text(f"استخدم الأمر {query.data} للقيام بـ {query.data.replace('_', ' ')}.")
    elif query.data in ['set_welcome', 'set_goodbye', 'set_rules', 'set_antispam', 'set_antiflood']:
        query.edit_message_text(f"استخدم الأمر {query.data} لتعيين {query.data.replace('set_', '')}.")

def main() -> None:
    """بدء البوت."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ban", ban))
    dispatcher.add_handler(CommandHandler("unban", unban))
    dispatcher.add_handler(CommandHandler("kick", kick))
    dispatcher.add_handler(CommandHandler("mute", mute))
    dispatcher.add_handler(CommandHandler("unmute", unmute))
    dispatcher.add_handler(CommandHandler("warn", warn))
    dispatcher.add_handler(CommandHandler("unwarn", unwarn))
    dispatcher.add_handler(CommandHandler("promote", promote))
    dispatcher.add_handler(CommandHandler("demote", demote))
    dispatcher.add_handler(CommandHandler("purge", purge))
    dispatcher.add_handler(CommandHandler("filter", filter_message))
    dispatcher.add_handler(CommandHandler("stop", stop_filter))
    dispatcher.add_handler(CommandHandler("filterlist", filter_list))
    dispatcher.add_handler(CommandHandler("gban", gban))
    dispatcher.add_handler(CommandHandler("lockall", lockall))
    dispatcher.add_handler(CommandHandler("unlockall", unlockall))
    dispatcher.add_handler(CommandHandler("dwarn", delete_and_warn))
    dispatcher.add_handler(CommandHandler("dmute", delete_and_mute))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("id", id_command))
    dispatcher.add_handler(CommandHandler("rules", rules))
    dispatcher.add_handler(CommandHandler("roll_dice", roll_dice))
    dispatcher.add_handler(CommandHandler("flip_coin", flip_coin))
    dispatcher.add_handler(CommandHandler("random_number", random_number))
    dispatcher.add_handler(CommandHandler("quote", quote))
    dispatcher.add_handler(CommandHandler("set_welcome", set_welcome))
    dispatcher.add_handler(CommandHandler("set_goodbye", set_goodbye))
    dispatcher.add_handler(CommandHandler("set_rules", set_rules))
    dispatcher.add_handler(CommandHandler("set_antispam", set_antispam))
    dispatcher.add_handler(CommandHandler("set_antiflood", set_antiflood))
    dispatcher.add_handler(CommandHandler("announcement", announcement))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print(f"🌼 بوت ديزي قيد التشغيل الآن! بواسطة {OWNER_USERNAME}")
    main()
