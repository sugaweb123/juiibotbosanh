import os
import time
import asyncio
import pyotp
import pyperclip
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest  # ✅ Added for timeout control


BOT_TOKEN = "7089691671:AAHjadzQycTnvykfdUA82JmT0Nh1yrgR4nU"
ALLOWED_USER_ID = 6878991479
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

username = "jl777"
password = "aa112233@@"
fator = "7O7KXBUPMNC2BAY4JJS7PK5XN3OHIVV4"

PLATFORMS = {
    "🧧Fuso77🧧":"Fuso777-10.6(9522)",
    "🧧Ginasio777🧧" : "Ginasio777-10.9(9523)",
    "平台🧧Porta777🧧" : "Porta777-10.13(9613)"
}

active_sessions = {}

print("Bot started...")


# --- Selenium job ---
def run_selenium(platform_name: str):
    driver = None
    try:
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": DOWNLOAD_DIR}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://0my9050g.offib.com/")
        time.sleep(15)

        # Login
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button").click()
        time.sleep(5)

        totp = pyotp.TOTP(fator)
        code = totp.now()
        driver.find_element(By.CSS_SELECTOR, "input[type='number']").send_keys(code)
        time.sleep(3)

        buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button")
        buttons[-1].click()
        time.sleep(8)

        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, ".el-icon-close")
            if not close_buttons:
                print("✅ No popup found, skipping...")
            else:
                print(f"🔴 Found {len(close_buttons)} popup(s), closing...")
                for btn in close_buttons:
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ Could not click popup: {e}")
        except Exception as e:
            print(f"⚠️ Error checking popups: {e}")

        arrow = driver.find_element(By.CSS_SELECTOR, "i.el-input__icon.el-icon-arrow-down")
        arrow.click()
        time.sleep(3)

        search_box = driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入名称或id搜索']")
        search_box.clear()
        search_box.send_keys(platform_name)
        time.sleep(1)

        buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button")
        buttons[-1].click()
        time.sleep(4)

        span_xpath = f"//section[contains(@class, 'canLogin')]//span[contains(text(), '{platform_name}')]"
        span_element = wait.until(EC.element_to_be_clickable((By.XPATH, span_xpath)))
        parent_div = span_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'M5IHUc47QOwYo6d2yoHZ')]")
        parent_div.click()
        time.sleep(5)

        close_btns = driver.find_elements(By.XPATH, "//span[contains(text(),' 关闭')]")
        if close_btns:
            close_btns[0].click()
            time.sleep(5)

        driver.find_element(By.XPATH, "//span[contains(text(),'代理')]").click()
        time.sleep(5)

        driver.find_element(By.XPATH, "//span[contains(text(),'代理数据查询(旧)')]").click()
        time.sleep(3)

        driver.find_element(By.XPATH, "//span[contains(text(),'搜索')]").click()
        time.sleep(3)

        driver.find_element(By.XPATH, "//span[contains(text(),' 导出报表')]").click()
        time.sleep(5)

        checkboxes = driver.find_elements(By.CSS_SELECTOR, "label.el-checkbox")
        for box in checkboxes:
            if "全选" in box.text.strip():
                ActionChains(driver).double_click(box).perform()
        time.sleep(2)

        fields = ['代理ID', '直属首充人次', '直属充值金额', '直属充值人次', '直属有效投注', '直属提现金额']
        for f in fields:
            driver.find_element(By.XPATH, f"//label[span[contains(text(),'{f}')]]").click()
            time.sleep(1)

        buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button")
        buttons[-1].click()
        time.sleep(15)

        driver.find_element(By.CLASS_NAME, "tags_drop_refreshBtn").click()
        time.sleep(15)

        copied_text = ""
        copy_btns = driver.find_elements(By.CSS_SELECTOR, "div.text-copy-container.no-padding")
        if copy_btns:
            copy_btns[0].click()
            time.sleep(1)
            copied_text = pyperclip.paste().strip()

        latest_file = None
        try:
            download_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[normalize-space(text())='下载']]"))
            )
            download_btn.click()
            time.sleep(10)

            downloaded_files = sorted(
                [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)],
                key=os.path.getmtime,
                reverse=True
            )
            if downloaded_files:
                latest_file = downloaded_files[0]
        except:
            pass

        driver.quit()
        time.sleep(3)  # ✅ small delay to ensure file finishes writing
        return copied_text, latest_file

    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        print(f"❌ Selenium error: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type == "private" and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("🤣🤣 bot ng  my boss b suga ot allow oy use private te b 🤣🤣.")
        return

    keyboard = [[InlineKeyboardButton(short, callback_data=short)] for short in PLATFORMS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Please choose a platform :", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    user = update.effective_user
    short_name = query.data
    platform_name = PLATFORMS[short_name]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notify_text = f"👤 User @{user.username or user.id} (ID: {user.id})\n" \
                  f"📅 Time: {now}\n" \
                  f"▶️ Ran platform: {platform_name}"
    await context.bot.send_message(ALLOWED_USER_ID, notify_text)

    if active_sessions.get(chat_id, False):
        await query.edit_message_text("⚠️ Bot is already running, please wait...")
        return

    active_sessions[chat_id] = True
    status_msg = await query.edit_message_text(f"⏳ waiting bot pg tver : {short_name} ...")

    copied_text, latest_file = run_selenium(platform_name)

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
    except:
        pass

    if copied_text is None and latest_file is None:
        await context.bot.send_message(chat_id, "❌ Bot error 👉 Please type /start again")
        active_sessions[chat_id] = False
        return

    if latest_file and os.path.isfile(latest_file):
        if copied_text:
            caption_text = f"\n```\n{copied_text}\n```\n🔴{short_name}🔴"
        else:
            caption_text = "❌ No password copied"

        with open(latest_file, "rb") as f:
            try:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption_text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                await context.bot.send_message(chat_id, f"⚠️ Upload failed: {e}\nRetrying...")
                await asyncio.sleep(5)
                with open(latest_file, "rb") as f2:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f2,
                        caption=caption_text,
                        parse_mode="Markdown"
                    )
    else:
        if copied_text:
            await context.bot.send_message(
                chat_id,
                text=f"✅ Password:\n```\n{copied_text}\n```",
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(chat_id, text="❌ No password copied")

        await context.bot.send_message(chat_id, "❌ No file downloaded")

    try:
        if update.effective_message:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
    except:
        pass

    active_sessions[chat_id] = False


# --- Main ---
def main():
    # ✅ Extend Telegram HTTP timeout to prevent TimedOut errors
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=30.0,
    )

    app = Application.builder().token(BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()


if __name__ == "__main__":
    main()

