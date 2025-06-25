import asyncio
import time
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

async def add_cloud_build_info(page, build_id):
    """Add Cloud Build info and timestamp to the page"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_text = f"Build ID: {build_id} | Time: {timestamp}"
    
    await page.evaluate('''(info) => {
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
    """Log in to GitHub using provided credentials"""
    try:
        print(f"Accessing GitHub login page...")
        await page.goto('https://github.com/login', timeout=10000, wait_until="networkidle")
        await page.wait_for_selector('#login_field')
        
        # Fill in credentials
        await page.fill('#login_field', username)
        await page.fill('#password', password)
        
        # Click sign in button
        await page.click('[name="commit"]')
        
        # Wait for login completion - check for dashboard or auth error
        await page.wait_for_selector('.shelf-title, .flash-error', timeout=10000)
        
        # Check for login errors
        if await page.query_selector('.flash-error'):
            error_message = await page.text_content('.flash-error')
            print(f"❌ Login failed: {error_message}")
            return False
            
        # Verify successful login by looking for profile avatar
        if await page.query_selector('.AppHeader-user'):
            print("✅ GitHub login successful")
            return True
        else:
            print("⚠️ Login status unknown - proceeding with caution")
            return True
    
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return False

async def convert_html_to_pdf(output_path: str, timeout: int = 30000):
    """Convert GitHub page to PDF after logging in"""
    build_id = os.getenv('BUILD_ID', 'local-build')
    
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Starting GitHub access...")
        start_time = time.time()
        
        try:
            # Retrieve credentials from environment or use provided defaults
            username = os.getenv('GITHUB_USERNAME', "abc.com")
            password = os.getenv('GITHUB_PASSWORD', "12345677")
            
            # Perform GitHub login
            login_success = await login_github(page, username, password)
            
            if not login_success:
                print("❌ Aborting PDF generation due to login failure")
                sys.exit(1)
            
            # Navigate to GitHub homepage after login
            print("Accessing GitHub dashboard...")
            await page.goto("https://github.com/", timeout=timeout, wait_until="networkidle")
            
            # Add build info and timestamp
            await add_cloud_build_info(page, build_id)
            await page.wait_for_timeout(1000)  # Ensure info renders
            
            # Generate PDF with GitHub-specific settings
            pdf_options = {
                "format": "A4",
                "print_background": True,
                "margin": {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                "display_header_footer": False,
                "scale": 0.8,
            }
            
            print(f"Generating PDF: {output_path}")
            await page.pdf(path=output_path, **pdf_options)
            print("✅ PDF generated successfully")
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            raise
        finally:
            await browser.close()
            
        elapsed = time.time() - start_time
        print(f"⏱️ Total execution time: {elapsed:.2f} seconds")

def ensure_output_directory(path: str):
    """Ensure output directory exists"""
    output_dir = Path(path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {output_dir}")

if __name__ == "__main__":
    output_path = "github.pdf"
    ensure_output_directory(output_path)
    
    try:
        asyncio.run(convert_html_to_pdf(output_path))
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
