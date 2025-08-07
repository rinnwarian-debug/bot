from instagrapi import Client
from instagrapi.types import UserShort
import time
import logging
import json
import os

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Налаштування клієнта Instagram
cl = Client()

# Файл для збереження оброблених користувачів
PROCESSED_FILE = "processed_users.json"

# Завантаження або ініціалізація оброблених користувачів
def load_processed_users():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('followers', [])), set(data.get('likers', []))
    return set(), set()

# Збереження оброблених користувачів
def save_processed_users(followers, likers):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump({'followers': list(followers), 'likers': list(likers)}, f)

# Повідомлення (одне для обох випадків)
MESSAGE = """Шукаєш сучасний, адаптивний та інтерактивний веб-сайт? Мій бот на зв’язку! 🚀

Я, MykyWEB, створюю веб-продукти, які вражають:
🌐 **HTML** — чітка та семантична структура для твого сайту.
🎨 **CSS (Flexbox, Grid)** — стильні, респонсивні макети, що ідеально виглядають на будь-якому пристрої.
⚡ **JavaScript** — динамічна інтерактивність: від плавних анімацій до потужних веб-додатків.

💡 **Чому обрати мене?**
- Індивідуальний підхід до кожного проєкту.
- Сучасні технології для швидкості, SEO та комфорту користувачів.
- Рішення, які піднімуть твій бізнес або особистий бренд.
- Швидка комунікація та підтримка 24/7.

Готовий до сайту, який вразить твоїх користувачів? Відвідай https://mykyweb.com і напиши мені! 📩 #WebDevelopment #MykyWeb

---

Looking for a modern, responsive, and interactive website? My bot’s got you covered! 🚀

I’m MykyWEB, and I create web products that impress:
🌐 **HTML** — clean and semantic structure for your site.
🎨 **CSS (Flexbox, Grid)** — stylish, responsive layouts that look perfect on any device.
⚡ **JavaScript** — dynamic interactivity, from smooth animations to powerful web apps.

💡 **Why choose me?**
- Tailored approach to every project.
- Cutting-edge tech for speed, SEO, and user comfort.
- Solutions to elevate your business or personal brand.
- Fast communication and 24/7 support.

Ready for a website that wows your users? Visit https://mykyweb.com and drop me a message! 📩 #WebDevelopment #MykyWeb

---

Hledáte moderní, responzivní a interaktivní web? Můj bot vám pomůže! 🚀

Jsem MykyWEB a tvořím webové produkty, které ohromí:
🌐 **HTML** — čistá a sémantická struktura pro váš web.
🎨 **CSS (Flexbox, Grid)** — stylové, responzivní rozvržení, které vypadá skvěle na každém zařízení.
⚡ **JavaScript** — dynamická interaktivita, od plynulých animací po výkonné webové aplikace.

💡 **Proč si vybrat mě?**
- Individuální přístup ke každému projektu.
- Moderní technologie pro rychlost, SEO a pohodlí uživatelů.
- Řešení, která posunou váš byznys nebo osobní značku na novou úroveň.
- Rychlá komunikace a podpora 24/7.

Připraveni na web, který okouzlí vaše uživatele? Navštivte https://mykyweb.com a napište mi! 📩 #WebDevelopment #MykyWeb"""

# Функція для обробки двофакторної автентифікації
def login_with_2fa():
    session_file = "session.json"
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login("myky_web", "PANKROCK1")
            logger.info("Успішний вхід із збереженої сесії")
        else:
            cl.login("myky_web", "PANKROCK1")
            cl.dump_settings(session_file)
            logger.info("Успішний вхід, сесію збережено")
    except Exception as e:
        if "Two-factor authentication required" in str(e):
            logger.info("Потрібна двофакторна автентифікація")
            verification_code = input("Введіть код 2FA (отриманий через SMS, email або додаток): ")
            try:
                cl.login("myky_web", "PANKROCK1", verification_code=verification_code)
                cl.dump_settings(session_file)
                logger.info("Успішний вхід із 2FA, сесію збережено")
            except Exception as e:
                logger.error(f"Помилка при вході з 2FA: {e}")
                raise
        else:
            logger.error(f"Помилка при вході: {e}")
            raise

# Функція для надсилання повідомлення
def send_message(user_id, message):
    try:
        cl.direct_send(message, [user_id])
        logger.info(f"Повідомлення надіслано користувачу {user_id}")
        return True
    except Exception as e:
        logger.error(f"Помилка при надсиланні повідомлення {user_id}: {e}")
        return False

# Функція для перевірки нових підписників
def check_new_followers(processed_followers):
    try:
        followers = cl.user_followers(cl.user_id)
        for follower in followers.values():
            if follower.pk not in processed_followers:
                if send_message(follower.pk, MESSAGE):
                    processed_followers.add(follower.pk)
                    time.sleep(10)  # Збільшена затримка
    except Exception as e:
        logger.error(f"Помилка при перевірці підписників: {e}")

# Функція для перевірки лайків на постах
def check_likes(processed_likers):
    try:
        posts = cl.user_medias(cl.user_id, amount=5)  # Перевіряємо останні 5 постів
        for post in posts:
            try:
                likers = cl.media_likers(post.id)
                for liker in likers:
                    if liker.pk not in processed_likers:
                        if send_message(liker.pk, MESSAGE):
                            processed_likers.add(liker.pk)
                            time.sleep(10)  # Збільшена затримка
            except Exception as e:
                logger.error(f"Помилка при перевірці лайків для поста {post.id}: {e}")
    except Exception as e:
        logger.error(f"Помилка при отриманні постів: {e}")

# Основний цикл бота
def main():
    logger.info("Бот запущено...")
    processed_followers, processed_likers = load_processed_users()
    
    try:
        login_with_2fa()
        while True:
            try:
                check_new_followers(processed_followers)
                check_likes(processed_likers)
                save_processed_users(processed_followers, processed_likers)
                logger.info("Очікування наступної перевірки...")
                time.sleep(600)  # Збільшено до 10 хвилин
            except KeyboardInterrupt:
                logger.info("Бот зупинено користувачем")
                save_processed_users(processed_followers, processed_likers)
                break
            except Exception as e:
                logger.error(f"Помилка в основному циклі: {e}")
                time.sleep(1800)  # Затримка 30 хвилин при помилці
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
        save_processed_users(processed_followers, processed_likers)

if __name__ == "__main__":
    main()