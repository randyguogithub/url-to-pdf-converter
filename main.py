import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def convert_html_to_pdf(url: str, output_path: str):
    """
    将指定URL的HTML页面转换为PDF
    
    参数:
        url (str): 要访问的网页URL
        output_path (str): 输出PDF的文件路径
    """
    async with async_playwright() as p:
        # 启动无头浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"正在访问页面: {url}")
        try:
            # 访问URL并等待页面完全加载
            await page.goto(url, wait_until="networkidle")
            
            # 添加额外的等待时间确保页面渲染完成
            await page.wait_for_timeout(3000)  # 等待3秒
            
            # 检测并处理潜在的不兼容元素
            page_has_complex_content = await evaluate_page_complexity(page)
            
            # 根据页面复杂性调整PDF生成选项
            pdf_options = {
                "format": "A4",
                "print_background": True,
                "margin": {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
            }
            
            if page_has_complex_content:
                print("检测到复杂页面元素，优化PDF转换设置...")
                pdf_options["displayHeaderFooter"] = True
                pdf_options["headerTemplate"] = "<div></div>"
                pdf_options["footerTemplate"] = "<div></div>"
            
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

async def evaluate_page_complexity(page) -> bool:
    """
    评估页面复杂性，检测可能引起问题的元素
    
    返回:
        bool: 如果页面包含可能不兼容的元素则返回True
    """
    complexity_factors = [
        # 检测WebGL/3D内容
        await page.evaluate('''() => {
            return !!document.querySelector('canvas') && 
                  (document.querySelector('canvas').getContext('webgl') || 
                   document.querySelector('canvas').getContext('experimental-webgl'));
        }'''),
        
        # 检测视频元素
        await page.evaluate('''() => document.querySelector('video') !== null'''),
        
        # 检测复杂的CSS动画
        await page.evaluate('''() => {
            const hasComplexAnimations = [...document.styleSheets].some(sheet => {
                try {
                    const rules = sheet.cssRules || [];
                    return [...rules].some(rule => 
                        rule.type === CSSRule.KEYFRAMES_RULE || 
                        rule.type === CSSRule.WEBKIT_KEYFRAMES_RULE
                    );
                } catch (e) { return false; }
            });
            return hasComplexAnimations;
        }'''),
        
        # 检测Web Workers
        await page.evaluate('''() => {
            const scripts = [...document.querySelectorAll('script')];
            return scripts.some(script => {
                const content = script.textContent.toLowerCase();
                return content.includes('worker') || content.includes('new worker');
            });
        }''')
    ]
    
    # 如果有任何因素存在，则视为复杂页面
    return any(complexity_factors)

if __name__ == "__main__":
    # 示例使用: 转换Google首页
    url = "https://www.github.com"
    output_path = "github.pdf"
    
    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    asyncio.run(convert_html_to_pdf(url, output_path))
