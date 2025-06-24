from browser_use.browser import Browser
import asyncio
from playwright.async_api import async_playwright
import os
import time
from img2pdf import convert

def run_job():
    print("Initializing browser...")
    browser = Browser(headless=True)  # 无头模式适合Cloud环境
    
    # 执行浏览器自动化任务
    browser.run("go to https://www.google.com")  # 打开指定URL
    time.sleep(3)  # 等待页面加载
    
    print("Capturing screenshot...")
    screenshot_path = "screenshot.png"
    browser.run(f"screenshot to {screenshot_path}")  # 截图保存
    
    browser.close()  # 关闭浏览器
    
    # 转换为PDF
    print("Converting to PDF...")
    with open(screenshot_path, "rb") as img_file:
        pdf_bytes = convert(img_file.read())
    
    pdf_path = "output.pdf"
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(pdf_bytes)
    
    print(f"PDF saved at {os.path.abspath(pdf_path)}")

if __name__ == "__main__":
    run_job()