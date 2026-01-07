import numpy as np
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import sys

class NYSudoku():
    def __init__(self,url):
        self._url = url
        self._board = None
        self._solution = None
    
    async def load(self):
        self._board = await self.getboard()
        print("Board Downloaded")
        self._solution = solve(self._board)
        print("Solution Generated")

    async def gethtml(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(self._url, wait_until="networkidle")

            html = await page.content()

            await browser.close()

        return html

    async def getboard(self):
        html = await self.gethtml()
        soup = BeautifulSoup(html, "html.parser")
        board = []
        index = 0
        while len(soup.find_all("div", {"data-testid": f"sudoku-cell-{index}"})) >0:
            board.append(soup.find_all("div", {"data-testid": f"sudoku-cell-{index}"})[0].get("aria-label"))
            index += 1

        board = np.array(board)
        board = board.astype(object)
        board = np.array([int(x) if x != 'empty' else None for x in board], dtype=object)
        n = int(np.sqrt(board.size))
        board = np.array(board)
        board = board.reshape(n,n)

        return (board)


def chunkify(board:np.array):
    H,W = board.shape
    sq = int(H ** 0.5)
    return board.reshape(sq,sq,sq,sq).swapaxes(1, 2).reshape(sq ** 2,sq ** 2)

def verify(board):
    for row in board:
        if True in (np.unique(row[row != None],return_counts=True)[1] > 1):
            return False
    for column in np.transpose(board):
        if True in (np.unique(column[column != None],return_counts=True)[1] > 1):
            return False
    for block in chunkify(board):
        if True in (np.unique(block[block != None],return_counts=True)[1] > 1):
            return False
    return True

def solve(board):
    for ri,row in enumerate(board):
        for vi,value in enumerate(row):
            if value is None:
                for i in range(1,len(board)+1):
                    board = np.array(board)
                    board[ri][vi] = i
                    if verify(board):
                        showboard(board)
                        result = solve(board)
                        if result is not None:
                            return result
                return None
    if verify (board):
        return board
    return None

def format_board(board):
    """Return a string of the board, one row per line."""
    lines = []
    for row in board:
        # replace None with . for empty cells
        line = " ".join(str(num) if num is not None else "." for num in row)
        lines.append(line)
    return "\n".join(lines)

def showboard(board):
    print(format_board(board))
    if not(all(all(cell is not None for cell in row) for row in board)):
        print(f"\033[{len(board)}A", end="")
