import sqlite3
import logging
from telegram import Update, ChatPermissions, ParseMode
from telegram.ext import (Updater, MessageHandler, Filters, CallbackContext, 
                          ConversationHandler, CommandHandler)

# --- الإعدادات ---
TOKEN = "YOUR_BOT_TOKEN" # ضع توكن بوتك هنا
OWNER_ID = 123456789    # ضع معرفك (ID) هنا

# حالات المحادثة لأمر (اضف امر)
GET_OLD, GET_NEW = range(2)

# الرتب الهرمية
ROLES_HIERARCHY = [
    "مطور اساسي", "مطور ثانوي", "مطور", 
    "منشئ اساسي", "منشئ", "مدير", 
    "ادمن", "مميز", "عضو"
]

# --- 1. قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('daisy_final.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS roles (user_id INTEGER PRIMARY KEY, role_name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS shortcuts (trigger TEXT PRIMARY KEY, target_cmd TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS stats (user_id INTEGER PRIMARY KEY, msg_count INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

def get_user_role(user_id):
    if user_id == OWNER_ID: return "مطور اساسي"
    conn = sqlite3.connect('daisy_final.db')
    c = conn.cursor()
    c.execute("SELECT role_name FROM roles WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else "عضو"

# --- 2. محادثة إضافة الاختصارات ---
def start_add_shortcut(update: Update, context: CallbackContext):
    if get_user_role(update.effective_user.id) != "مطور اساسي": return ConversationHandler.END
    update.message.reply_text("📥 ما هو الأمر القديم؟\n(مثال: رفع مطور اساسي)")
    return GET_OLD

def get_old_cmd(update: Update, context: CallbackContext):
    context.user_data['old_cmd'] = update.message.text.strip()
    update.message.reply_text(f"✅ تم اختيار: {context.user_data['old_cmd']}\nالآن أرسل الاختصار الجديد:")
    return GET_NEW

def get_new_shortcut(update: Update, context: CallbackContext):
    new_trigger = update.message.text.strip()
    old_cmd = context.user_data['old_cmd']
    conn = sqlite3.connect('daisy_final.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO shortcuts VALUES (?, ?)", (new_trigger, old_cmd))
    conn.commit()
    conn.close()
    update.message.reply_text(f"✨ تم الحفظ! `{new_trigger}` أصبح يؤدي لـ `{old_cmd}`")
    return ConversationHandler.END

# --- 3. المعالج الرئيسي للأوامر ---
def main_handler(update: Update, context: CallbackContext):
    if not update.message or not update.message.text: return
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    
    # تحديث عداد الرسائل
    conn = sqlite3.connect('daisy_final.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO stats (user_id, msg_count) VALUES (?, 0)", (user.id,))
    c.execute("UPDATE stats SET msg_count = msg_count + 1 WHERE user_id = ?", (user.id,))
    conn.commit()
    
    # فحص الاختصارات
    c.execute("SELECT target_cmd FROM shortcuts WHERE trigger = ?", (text.split()[0],))
    res = c.fetchone()
    conn.close()
    
    cmd_text = res[0] if res else text
    parts = cmd_text.split()
    cmd = parts[0]
    
    role = get_user_role(user.id)

    # --- [أمر الأيدي المطور] ---
    if cmd in ["ايدي", "ايديدي"]:
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else user
        
        conn = sqlite3.connect('daisy_final.db')
        c = conn.cursor()
        c.execute("SELECT msg_count FROM stats WHERE user_id = ?", (target.id,))
        m_res = c.fetchone()
        conn.close()
        
        msgs = m_res[0] if m_res else 0
        username = f"@{target.username}" if target.username else "لا يوجد"
        
        caption = (
            f"˛ َ𝖲𝗍ُɑِ  : {target.first_name}\n"
            f"˛ َ𝖴ᥱ᥉ : {username}\n"
            f"˛ َ𝖨ժ : `{target.id}`\n"
            f"˛ َ𝖬⁪⁬⁮᥉𝗀ِ : {msgs}"
        )
        
        try:
            photos = context.bot.get_user_profile_photos(target.id, limit=1)
            if photos.total_count > 0:
                update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN)
        except:
            update.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN)

    # --- [أوامر الرفع] ---
    elif cmd_text.startswith("رفع "):
        new_role = cmd_text.replace("رفع ", "").strip()
        if new_role in ROLES_HIERARCHY and update.message.reply_to_message:
            idx_s = ROLES_HIERARCHY.index(role)
            idx_t = ROLES_HIERARCHY.index(new_role)
            if idx_s < idx_t or role == "مطور اساسي":
                target_user = update.message.reply_to_message.from_user
                conn = sqlite3.connect('daisy_final.db')
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO roles (user_id, role_name) VALUES (?, ?)", (target_user.id, new_role))
                conn.commit()
                conn.close()
                update.message.reply_text(f"✅ تم رفع {target_user.first_name} لـ {new_role}")

    # --- [أمر مسح] ---
    elif cmd == "مسح":
        is_admin = context.bot.get_chat_member(chat_id, user.id).status in ['creator', 'administrator'] or role == "مطور اساسي"
        if is_admin:
            try:
                update.message.delete()
                num = int(parts[1]) if len(parts) > 1 else 1
                for i in range(num):
                    try: context.bot.delete_message(chat_id, update.message.message_id - (i + 1))
                    except: continue
            except: pass

    # --- [أمر رتبتي والتنزيل] ---
    elif cmd_text == "رتبتي":
        update.message.reply_text(f"🎖️ رتبتك: *{role}*", parse_mode=ParseMode.MARKDOWN)
    
    elif cmd_text == "تنزيل" and update.message.reply_to_message:
        target_u = update.message.reply_to_message.from_user
        conn = sqlite3.connect('daisy_final.db')
        c = conn.cursor()
        c.execute("DELETE FROM roles WHERE user_id = ?", (target_u.id,))
        conn.commit()
        conn.close()
        update.message.reply_text(f"📉 تم تنزيل {target_u.first_name} لعضو")

def run():
    init_db()
    u = Updater(TOKEN)
    dp = u.dispatcher
    
    # محادثة الإضافة
    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^اضف امر$'), start_add_shortcut)],
        states={
            GET_OLD: [MessageHandler(Filters.text & ~Filters.command, get_old_cmd)],
            GET_NEW: [MessageHandler(Filters.text & ~Filters.command, get_new_shortcut)],
        },
        fallbacks=[MessageHandler(Filters.regex('^الغاء$'), lambda u,c: ConversationHandler.END)],
    )
    
    dp.add_handler(conv)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, main_handler))
    
    print("✅ البوت يعمل الآن..")
    u.start_polling()
    u.idle()

if __name__ == '__main__':
    run()
