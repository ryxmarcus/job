import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        page = await ctx.new_page()
        url = 'https://135135392458-a7gpftpe.ap-south-1.console.aws.amazon.com/ec2/home?region=ap-south-1#InstanceDetails:instanceId=i-056339ce277361fdb'
        print(f"Navigating to AWS Console: {url}...")
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=25000)
            await asyncio.sleep(4)
            print("Title:", await page.title())
            print("Current URL:", page.url)
            body = await page.inner_text('body')
            print("Snippet:\n", body[:600].replace('\n', ' -- '))
            
            # Check for Public IP address or Public DNS on the page
            for line in body.split('\n'):
                if any(w in line.lower() for w in ['public ipv4', 'public ip', 'elastic ip', 'dns']):
                    print("IP/DNS LINE:", line.strip())

        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    asyncio.run(main())

