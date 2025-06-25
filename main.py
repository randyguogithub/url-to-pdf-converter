import asyncio
from playwright.async_api import async_playwright
import img2pdf
import os

async def capture_webpage(url, output_pdf):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 导航到目标网址
        await page.goto(url)
        await page.wait_for_timeout(3000)  # 等待页面加载
        
        # 截图保存为临时图片
        screenshot_path = "screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        await browser.close()
        
        # 转换为PDF
        with open(screenshot_path, "rb") as img_file:
            img_data = img_file.read()
        
        pdf_bytes = img2pdf.convert(img_data)
        
        with open(output_pdf, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        
        # 清理临时文件
        os.remove(screenshot_path)
        print(f"PDF 已保存到 {os.path.abspath(output_pdf)}")

if __name__ == "__main__":
    # 测试调用
    asyncio.run(capture_webpage("https://www.github.com", "github.pdf"))
