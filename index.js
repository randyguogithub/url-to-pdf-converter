const puppeteer = require('puppeteer');

async function generatePdf(url, outputPath) {
    console.log(`Attempting to generate PDF for URL: ${url} to ${outputPath}`);
    let browser;
    try {
        browser = await puppeteer.launch({
            // headless: true is the default for new Puppeteer versions.
            // Explicitly set for clarity if needed: headless: 'new' or headless: true
            args: [
                '--no-sandbox', // Essential for Docker environments like Cloud Build
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage', // Recommended for Docker environments
                '--disable-notifications',
                '--disable-gpu' // Recommended if not using hardware acceleration
            ]
        });
        const page = await browser.newPage();

        // Optional: Set a specific user agent if needed
        // await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 BroswerScreenshotter/1.0');

        await page.goto(url, {
            waitUntil: 'networkidle0', // Wait until no more than 0 network connections for at least 500ms
            timeout: 60000 // Increase timeout to 60 seconds for potentially slow pages
        });

        // Optional: Wait for a specific selector to appear to ensure content is loaded
        // await page.waitForSelector('body', { timeout: 10000 });

        // Generate PDF
        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true, // Include background colors/images
            displayHeaderFooter: false, // Don't show default headers/footers
            margin: { // Reduce margins to maximize content
                top: '0.5in',
                right: '0.5in',
                bottom: '0.5in',
                left: '0.5in'
            }
        });

        console.log(`PDF generated successfully at: ${outputPath}`);
    } catch (error) {
        console.error(`Error generating PDF for ${url}:`, error);
        process.exit(1); // Exit with an error code
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Get URL and output filename from environment variables
const targetUrl = process.env.TARGET_URL;
const outputFilename = process.env.OUTPUT_FILENAME;

if (!targetUrl || !outputFilename) {
    console.error('Usage: TARGET_URL and OUTPUT_FILENAME environment variables must be set.');
    process.exit(1);
}

const outputPath = `/tmp/${outputFilename}`; // Always write to /tmp in Cloud Build

generatePdf(targetUrl, outputPath);
