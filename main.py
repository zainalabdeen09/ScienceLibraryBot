import asyncio
import logging
import os
import tempfile

import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from books_db import BOOKS_DB, search_db, get_branch_books

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN", "8795744717:AAH-fAbRJGn84lCRIZpBj9T4-4rzpnYIsX0")

bot = Bot(token=TOKEN)
dp = Dispatcher()

_chat_data: dict[int, dict] = {}


def main_menu_kb():
    kb = []
    for name in BOOKS_DB:
        kb.append([InlineKeyboardButton(text=name, callback_data=f"br_{name}")])
    kb.append([InlineKeyboardButton(text="🔍 بحث مخصص", callback_data="custom_search")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def book_list_kb(books: list, start: int = 0):
    kb = []
    for i, b in enumerate(books[start:start+5], start):
        kb.append([InlineKeyboardButton(
            text=f"📥 {i+1}. {b['title'][:30]} | {b['size']}",
            callback_data=f"dl_{i}"
        )])
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton(text="⏪ السابق", callback_data=f"prv_{start-5}"))
    if len(books) > start + 5:
        nav.append(InlineKeyboardButton(text="التالي ⏩", callback_data=f"nxt_{start+5}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="bk_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "<b>🧪 مكتبة الكيمياء | Chemistry Library</b>\n\n"
        "اختر فرع الكيمياء 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "<b>مكتبة الكيمياء</b>\n"
        "اختر فرع ← اختر كتاب ← التحميل التلقائي\n"
        "أو اكتب اسم كتاب للبحث\n\n"
        "تم التطوير بواسطة @za_c10",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@dp.callback_query(F.data.startswith("br_"))
async def branch_callback(callback: types.CallbackQuery):
    branch = callback.data[3:]
    books = get_branch_books(branch)
    if not books:
        await callback.message.edit_text(
            f"لا توجد كتب في {branch}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 القائمة", callback_data="bk_main")],
            ]),
        )
        await callback.answer()
        return
    chat_id = callback.message.chat.id
    _chat_data[chat_id] = {"books": books, "title": branch}
    text = f"<b>{branch}</b>\n"
    for i, b in enumerate(books[:5], 1):
        text += f"\n<b>{i}.</b> {b['title'][:40]}\n   👤 {b['author'][:20]} | 📦 {b['size']}"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=book_list_kb(books))
    await callback.answer()


@dp.callback_query(F.data == "custom_search")
async def custom_search_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔍 <b>بحث مخصص</b>\n\n"
        "أرسل اسم الكتاب اللي تبحث عنه\n"
        "مثال: <code>organic chemistry</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 القائمة", callback_data="bk_main")],
        ]),
    )
    await callback.answer()


@dp.callback_query(F.data == "bk_main")
async def back_main_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    _chat_data.pop(chat_id, None)
    await callback.message.edit_text(
        "<b>🧪 مكتبة الكيمياء | Chemistry Library</b>\n\n"
        "اختر فرع الكيمياء 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@dp.callback_query(F.data.startswith("nxt_"))
async def next_page_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    data = _chat_data.get(chat_id)
    if not data:
        await callback.answer("انتهت الجلسة، ارجع للقائمة", show_alert=True)
        return
    start = int(callback.data[4:])
    books = data["books"]
    text = f"<b>{data['title']}</b>\n"
    for i, b in enumerate(books[start:start+5], start):
        text += f"\n<b>{i+1}.</b> {b['title'][:40]}\n   👤 {b['author'][:20]} | 📦 {b['size']}"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=book_list_kb(books, start))
    await callback.answer()


@dp.callback_query(F.data.startswith("prv_"))
async def prev_page_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    data = _chat_data.get(chat_id)
    if not data:
        await callback.answer("انتهت الجلسة", show_alert=True)
        return
    start = int(callback.data[4:])
    books = data["books"]
    text = f"<b>{data['title']}</b>\n"
    for i, b in enumerate(books[start:start+5], start):
        text += f"\n<b>{i+1}.</b> {b['title'][:40]}\n   👤 {b['author'][:20]} | 📦 {b['size']}"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=book_list_kb(books, start))
    await callback.answer()


@dp.callback_query(F.data.startswith("dl_"))
async def download_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    data = _chat_data.get(chat_id)
    if not data:
        await callback.answer("انتهت الجلسة، ارجع واختر كتاباً", show_alert=True)
        return
    idx = int(callback.data[3:])
    books = data["books"]
    if idx < 0 or idx >= len(books):
        await callback.answer("خطأ في اختيار الكتاب", show_alert=True)
        return
    book = books[idx]
    await callback.answer()
    await callback.message.answer(f"⏳ جاري تجهيز <b>{book['title']}</b>...", parse_mode="HTML")
    await send_book(chat_id, book)


async def send_book(chat_id: int, book: dict):
    ia_id = book.get("ia_id", "")
    if not ia_id:
        await bot.send_message(chat_id, "❌ هذا الكتاب لا يحتوي على رابط تحميل")
        return

    caption = f"<b>{book['title']}</b>\n👤 {book['author']}\n📦 {book['size']} | {book['year']}"

    # Step 1: Find real PDF filenames via IA metadata API
    pdf_names = [f"{ia_id}.pdf", f"{ia_id}_text.pdf"]
    try:
        async with aiohttp.ClientSession() as session:
            meta_url = f"https://archive.org/metadata/{ia_id}"
            async with session.get(meta_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    import json
                    meta = await resp.json()
                    files = meta.get("files", [])
                    found = [f["name"] for f in files if f.get("name", "").lower().endswith(".pdf")]
                    if found:
                        pdf_names = found
                        logging.info(f"IA '{ia_id}': found PDFs {found[:3]}")
    except Exception as e:
        logging.warning(f"IA metadata fail for {ia_id}: {e}")

    MAX_SIZE = 48 * 1024 * 1024

    # Step 2: Try downloading from archive.org and sending
    for pdf_name in pdf_names:
        url = f"https://archive.org/download/{ia_id}/{pdf_name}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                    if resp.status != 200:
                        continue
                    length = resp.content_length
                    if length and length > MAX_SIZE:
                        logging.info(f"Skip {pdf_name}: {length} bytes > 48MB")
                        continue
                    content = await resp.read()
                    if len(content) < 50000:
                        continue
                    if len(content) > MAX_SIZE:
                        logging.info(f"Skip {pdf_name}: downloaded {len(content)} bytes > 48MB")
                        continue
                    safe_name = f"{ia_id}.pdf"
                    tmp = os.path.join(tempfile.gettempdir(), safe_name)
                    with open(tmp, "wb") as f:
                        f.write(content)
                    inp = FSInputFile(tmp, filename=safe_name)
                    await bot.send_document(chat_id, inp, caption=caption, parse_mode="HTML")
                    os.unlink(tmp)
                    logging.info(f"Sent: {url}")
                    return
        except Exception as e:
            logging.warning(f"DL fail {pdf_name}: {e}")
            continue

    # Step 3: Try URL-based send for small files (<20MB)
    for url in [
        f"https://archive.org/download/{ia_id}/{ia_id}.pdf",
        f"https://archive.org/download/{ia_id}/{ia_id}_text.pdf",
    ]:
        try:
            await bot.send_document(chat_id, document=url, caption=caption, parse_mode="HTML")
            logging.info(f"Sent via URL: {url}")
            return
        except Exception:
            pass

    # Step 4: Fallback - show link
    link = f"https://archive.org/details/{ia_id}"
    await bot.send_message(
        chat_id,
        f"⚠️ الملف كبير جداً (أكثر من 50MB)\n📎 الرابط:\n{link}",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📂 فتح الرابط", url=link)],
            [InlineKeyboardButton(text="🔙 القائمة", callback_data="bk_main")],
        ]),
    )


@dp.message(Command("update"))
async def cmd_update(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ الأمر متاح للمالك فقط")
        return
    await message.answer("🔄 جاري تحديث قاعدة البيانات من Archive.org... قد يستغرق دقائق")
    try:
        from discover_books import discover_and_save
        import books_db
        stats = await discover_and_save()
        books_db.reload_from_json()
        import sys
        this = sys.modules[__name__]
        this.BOOKS_DB = books_db.BOOKS_DB
        total = sum(len(v) for v in BOOKS_DB.values())
        msg = f"✅ تم التحديث!\n📚 إجمالي الكتب: {total}\n"
        for k, v in stats.items():
            msg += f"• {k}: {v} كتب\n"
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ فشل التحديث: {e}")
        logging.exception("Update failed")

@dp.message(Command("search"))
async def cmd_search(message: types.Message):
    query = message.text.replace("/search", "", 1).strip()
    if not query:
        await message.answer("مثال: <code>/search organic chemistry</code>", parse_mode="HTML")
        return
    await perform_search(message, query)


@dp.message()
async def text_search(message: types.Message):
    if message.text and not message.text.startswith("/"):
        await perform_search(message, message.text)


async def perform_search(msg, query):
    wait = await msg.answer(f"🔍 جاري البحث عن <b>{query}</b>...", parse_mode="HTML")
    results = search_db(query)
    await wait.delete()
    if not results:
        await msg.answer(
            f"😕 لا توجد نتائج لـ <b>{query}</b> في المكتبة\n"
            "💡 جرب كلمات أخرى أو اختر فرعاً من القائمة",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="bk_main")],
            ]),
        )
        return
    chat_id = msg.chat.id
    _chat_data[chat_id] = {"books": results, "title": f"نتائج: {query}"}
    text = f"<b>نتائج: {query}</b>\n"
    for i, b in enumerate(results[:5], 1):
        text += f"\n<b>{i}.</b> {b['title'][:40]}\n   👤 {b['author'][:20]} | 📦 {b['size']}"
    await msg.answer(text, parse_mode="HTML", reply_markup=book_list_kb(results))


async def main():
    logging.info("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
