import asyncio
import time
from playwright.async_api import async_playwright
from pathlib import Path

async def convert_html_to_pdf(url: str, output_path: str, timeout: int = 30000):
    """
    将指定URL的HTML页面转换为PDF
    
    参数:
        url (str): 要访问的网页URL
        output_path (str): 输出PDF的文件路径
        timeout (int): 页面加载超时时间（毫秒）
    """
    async with async_playwright() as p:
        # 启动无头浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"访问页面: {url}")
        try:
            # 访问URL并等待页面完全加载
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            
            # 添加额外的等待时间确保页面渲染完成
            await page.wait_for_timeout(2000)  # 等待2秒
            
            # 简化PDF参数设置
            pdf_options = {
                "format": "A4",
                "print_background": True,
                "margin": {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                "display_header_footer": False  # 默认为不显示页眉页脚
            }
            
            # 对于特定网站应用定制设置
            if "github.com" in url:
                print("GitHub页面检测，应用特定PDF设置...")
                pdf_options["scale"] = 0.8
                await page.emulate_media(media="screen")
            
            # 生成PDF
            print(f"生成PDF文件: {output_path}")
            await page.pdf(path=output_path, **pdf_options)
            print("PDF生成成功")
            
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
            raise
        finally:
            # 确保关闭浏览器
            await browser.close()

def ensure_output_directory(path: str):
    """确保输出目录存在"""
    output_dir = Path(path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"创建输出目录: {output_dir}")

if __name__ == "__main__":
    # 网站列表处理
    urls = [
        "https://www.github.com"
    ]
    
    for url in urls:
        try:
            # 生成安全的文件名
            domain = url.split("//")[-1].split("/")[0].replace(".", "_")
            output_path = f"github.pdf"
            
            # 确保输出目录存在
            ensure_output_directory(output_path)
            
            print(f"开始处理: {url}")
            start_time = time.time()
            
            # 运行转换任务
            asyncio.run(convert_html_to_pdf(url, output_path))
            
            elapsed = time.time() - start_time
            print(f"处理完成: {url} (耗时: {elapsed:.2f}秒)")
            print("-" * 50)
            
        except Exception as e:
            print(f"处理 {url} 失败: {str(e)}")
