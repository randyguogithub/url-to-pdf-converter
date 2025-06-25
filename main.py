import asyncio
import time
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

async def add_cloud_build_info(page, build_id, login_status):
    """添加Cloud Build信息和时间戳到页面"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_text = "✅ Login Successful" if login_status else "❌ Login Failed"
    info_text = f"Build ID: {build_id} | Time: {timestamp} | Status: {status_text}"
    
    await page.evaluate('''(info) => {
        const existingInfo = document.getElementById('cloud-build-info');
        if (existingInfo) existingInfo.remove();
        
        const container = document.createElement('div');
        container.id = 'cloud-build-info';
        container.style.position = 'fixed';
        container.style.bottom = '10px';
        container.style.right = '10px';
        container.style.backgroundColor = 'rgba(0,0,0,0.7)';
        container.style.color = 'white';
        container.style.padding = '5px 10px';
        container.style.borderRadius = '4px';
        container.style.fontFamily = 'Arial, sans-serif';
        container.style.fontSize = '12px';
        container.style.zIndex = '9999';
        container.style.textAlign = 'center';
        container.innerText = info;
        document.body.appendChild(container);
    }''', info_text)

async def login_github(page, username, password):
    """登录GitHub并报告所有遇到的情况"""
    login_status = False
    login_message = "No login attempt made"
    
    try:
        print("Accessing GitHub login page...")
        await page.goto('https://github.com/login', timeout=15000, wait_until="networkidle")
        await page.wait_for_selector('#login_field', timeout=5000)
        
        # 填写凭据
        await page.fill('#login_field', username)
        await page.fill('#password', password)
        
        # 点击登录按钮
        await page.click('[name="commit"]')
        
        # 等待登录结果
        await asyncio.sleep(2)  # 等待可能的页面跳转
        
        # 检查登录结果
        if await page.query_selector('.flash-error'):  # 登录失败消息
            login_message = await page.eval_on_selector('.flash-error', 'el => el.textContent.trim()')
            login_message = login_message.replace('×', '').strip()
            print(f"❌ Login failed: {login_message}")
        elif await page.query_selector('.AppHeader-user'):  # 登录成功元素
            login_status = True
            login_message = "Login successful"
            print("✅ GitHub login successful")
        elif await page.query_selector('[data-testid="login-button"]'):  # 仍然显示登录按钮
            login_message = "Still on login page - login may have failed"
            print("⚠️ Still on login page after login attempt")
        else:
            login_message = "Unknown login state - proceeding"
            print("⚠️ Login status unknown - proceeding")
            
    except Exception as e:
        login_message = f"Login attempt error: {str(e)}"
        print(f"❌ Error during login: {str(e)}")
    
    return login_status, login_message

async def process_page(page, target_url, timeout):
    """处理页面导航和PDF生成"""
    build_id = os.getenv('BUILD_ID', 'local-build')
    login_status = False
    login_message = ""
    
    # 从环境变量获取凭据
    username = os.getenv('GITHUB_USERNAME', "abc.com")
    password = os.getenv('GITHUB_PASSWORD', "12345677")
    
    # 执行GitHub登录
    login_status, login_message = await login_github(page, username, password)
    
    # 导航到目标URL（无论登录状态如何）
    print(f"Navigating to: {target_url}")
    try:
        await page.goto(target_url, timeout=timeout, wait_until="networkidle")
        print(f"Successfully navigated to {target_url}")
    except Exception as nav_error:
        login_message += f"\nNavigation error: {str(nav_error)}"
        print(f"❌ Navigation failed: {str(nav_error)}")
    
    # 添加构建信息（包括登录状态）
    await add_cloud_build_info(page, build_id, login_status)
    await page.wait_for_timeout(1000)  # 确保信息渲染
    
    # 生成PDF的设置
    pdf_options = {
        "format": "A4",
        "print_background": True,
        "margin": {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
        "display_header_footer": False,
        "scale": 0.8,
    }
    
    return login_status, login_message, pdf_options

async def convert_html_to_pdf(output_path: str, timeout: int = 30000):
    """将GitHub页面转换为PDF，并处理所有登录状态"""
    async with async_playwright() as p:
        # 启动无头浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Starting GitHub processing...")
        start_time = time.time()
        
        try:
            # 处理页面并获取登录状态
            login_status, login_message, pdf_options = await process_page(page, "https://github.com/", timeout)
            
            # 生成PDF
            print(f"Generating PDF: {output_path}")
            await page.pdf(path=output_path, **pdf_options)
            print("✅ PDF generated successfully")
            
            # 记录所有登录消息
            return login_status, login_message
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            raise
        finally:
            await browser.close()
            
        elapsed = time.time() - start_time
        print(f"⏱️ Total execution time: {elapsed:.2f} seconds")

def ensure_output_directory(path: str):
    """确保输出目录存在"""
    output_dir = Path(path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {output_dir}")

if __name__ == "__main__":
    output_path = "github.pdf"
    ensure_output_directory(output_path)
    
    try:
        login_status, login_message = asyncio.run(convert_html_to_pdf(output_path))
        print("\nProcessing completed with the following login results:")
        print(login_message)
        if login_status:
            print("✅ Login was successful")
        else:
            print("❌ Login failed or encountered issues")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
