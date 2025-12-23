import re
from playwright.async_api import async_playwright
import numpy as np
from NYSudoku import NYSudoku
import asyncio

Games = {
    "easy":"https://www.nytimes.com/puzzles/sudoku/easy",
    "medium":"https://www.nytimes.com/puzzles/sudoku/medium",
    "hard":"https://www.nytimes.com/puzzles/sudoku/hard"
}

async def play_board(board,url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.get_by_role("button", name="Reject all").click()
        await page.get_by_role("button", name="Close").click()
        await page.locator("body").press("ArrowRight")
        for index,row in enumerate(board):
            await page.get_by_test_id(f"sudoku-cell-{index*len(row)}").click()
            for value in row:
                await page.keyboard.press(str(value))
                await page.locator("body").press("ArrowRight")
        await asyncio.sleep(1)
        return
    

async def playall():
    games = [NYSudoku.NYSudoku(url) for url in Games.values()]
    for game in games:
        await game.load()
        await play_board(game._solution,game._url)

if __name__ == "__main__":
    asyncio.run(playall())