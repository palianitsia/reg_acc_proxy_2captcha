import asyncio
import random
import string
from playwright.async_api import async_playwright

async def save_account(email, username, password, domain):
    with open('accounts.txt', 'a') as f:
        f.write(f"{email}:{username}:{password}:{domain}\n")

async def generate_random_email():
    length = random.randint(7, 15)
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{random_string}@yopmail.com"

async def get_proxies():
    with open('proxy.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

async def get_usernames():
    with open('usern.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

async def register_account(domain, username, email, password, proxy):
    async with async_playwright() as p:
        browser = None
        try:
            # Avvia il browser
            browser_args = ['--disable-gpu', '--disable-dev-shm-usage', '--no-sandbox']
            browser = await p.chromium.launch(headless=False, args=browser_args)
            
            if proxy:
                context = await browser.new_context(
                    proxy={"server": proxy.split('@')[1], "username": proxy.split('@')[0].split(':')[0], "password": proxy.split('@')[0].split(':')[1]}
                )
            else:
                context = await browser.new_context()

            page = await context.new_page()

            await page.goto(f'https://{domain}.bidoo.com/Iscriviti-20-crediti.php')
            await page.wait_for_timeout(15000)
            
            await page.fill('input[name="em"]', email)
            await page.fill('input[name="un"]', username)
            await page.fill('input[name="pw"]', password)
            await page.check('input[type="checkbox"]')

            await page.click('#btnRegister')

            await page.wait_for_url(f'https://{domain}.bidoo.com/home_alt.php?onboard=false&nu=true')

            await save_account(email, username, password, domain)

            with open('usern.txt', 'r') as f:
                usernames = f.readlines()

            usernames = [line.strip() for line in usernames if line.strip() != username]

            with open('usern.txt', 'w') as f:
                f.write('\n'.join(usernames))

            print(f"Account registrato: {email}")
            print(f"Username rimosso: {username}")

            await browser.close()
            return

        except Exception as e:
            print(f"Errore durante la registrazione: {e}")
        finally:
            if browser:
                print("Il browser è ancora aperto per il debug.")
                await asyncio.sleep(50)
                await browser.close()

async def main():
    domain = input("Inserisci il dominio (it/es): ")
    quantity = int(input("Quanti account vuoi registrare? "))
    password = input("Inserisci la password (fissa o 'random' per una password casuale): ")
    
    if password.lower() == 'random':
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    use_proxy = input("Vuoi utilizzare un proxy? (s/n): ").lower() == 's'
    proxies = await get_proxies() if use_proxy else []
    usernames = await get_usernames()

    for _ in range(quantity):
        email = await generate_random_email()
        username = random.choice(usernames) if usernames else f"user_{random.randint(1000, 9999)}"
        proxy = random.choice(proxies) if use_proxy and proxies else None

        print(f"Registrando account: {username}, Email: {email}, Proxy: {proxy}")
        await register_account(domain, username, email, password, proxy)

if __name__ == "__main__":
    asyncio.run(main())
