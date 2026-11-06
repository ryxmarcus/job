import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'gemini' in page.url][0]

        res = await pg.evaluate("""() => {
            // Find what blocks belong to page 2
            let blocks = window.__NEXT_DATA__.props.pageProps.blocks;
            let page2Blocks = [];
            let inPage2 = false;
            for (let b of blocks) {
                if (b.type === 'PAGE' || b.type === 'PAGE_BREAK') {
                    if (inPage2) break;
                    inPage2 = true;
                    continue;
                }
                if (inPage2) {
                    page2Blocks.push({
                        type: b.type,
                        uuid: b.uuid,
                        groupUuid: b.groupUuid,
                        isRequired: b.payload?.isRequired
                    });
                }
            }
            return page2Blocks;
        }""")
        print("Page 2 blocks summary:")
        for b in res:
            if b.get('isRequired') or b['type'] in ['TITLE', 'RANKING_OPTION', 'MULTIPLE_CHOICE_OPTION']:
                print(" ", b)

if __name__ == '__main__':
    asyncio.run(main())

