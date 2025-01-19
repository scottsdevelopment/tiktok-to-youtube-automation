# TikTok to YouTube Automation

![GitHub issues](https://img.shields.io/github/issues/scottsdevelopment/tiktok-to-youtube-automation)  
![GitHub license](https://img.shields.io/github/license/scottsdevelopment/tiktok-to-youtube-automation)  
![GitHub stars](https://img.shields.io/github/stars/scottsdevelopment/tiktok-to-youtube-automation)

## Overview

This project provides a fully automated workflow to download TikTok videos, extract metadata, and upload the content directly to YouTube Shorts. It simplifies cross-platform content sharing for creators and aims to minimize manual effort. Perfect for individuals and organizations managing multi-platform content distribution.

---

### Features

- **Automated TikTok Downloads**: Retrieve videos and metadata from TikTok.
- **YouTube Shorts Uploads**: Post videos with customizable titles, descriptions, and tags.
- **User-Friendly Configuration**: Easy setup and authentication process.
- **Metadata Extraction**: Automatically extract captions and links from TikTok videos.
- **Error Handling**: Built-in mechanisms for retrying failed uploads.

---

### Installation

#### Prerequisites

1. Install Python 3.8 or newer.
2. Install Node.js and npm (for TikTok scraper).
3. Set up Google Cloud Console for YouTube Data API v3.

#### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/your-org/tiktok-to-youtube-automation.git
   cd tiktok-to-youtube-automation
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install TikTok scraper:
   ```bash
   npm install -g tiktok-scraper
   ```

4. Configure YouTube API credentials:
   - Create a project on [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the YouTube Data API v3.
   - Download `client_secrets.json` and place it in the `resources/` directory.

---

### Usage

1. **Set Configuration**:
   - Open `main.py` and replace `TIKTOK_USERNAME` with the desired TikTok username.
   - Ensure the `client_secrets.json` file is correctly placed.

2. **Run the Script**:
   ```bash
   python main.py
   ```

3. **Authenticate**:
   - Follow the OAuth flow in your browser to authenticate with YouTube.
   - Once authenticated, the script will start downloading TikTok videos and uploading them to YouTube Shorts.

---

### Repository Structure

```
.
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── main.py
├── resources/
│   ├── client_secrets.json
│   └── examples/
│       ├── metadata_example.json
│       └── video_example.mp4
```

---

### Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request on GitHub.

---

### License

This project is licensed under the [MIT License](LICENSE).

---

### Contact

For questions, support, or feedback, open an issue on GitHub or email the maintainers.

---

### Future Enhancements

- **Multiple Account Support**: Allow downloading and uploading from multiple TikTok accounts.
- **Video Editing Options**: Add trimming, watermarking, and resizing features.
- **CLI Configuration**: Implement an interactive command-line tool for configuration.
- **Automated Scheduling**: Enable regular updates for new TikTok content.
- **Cloud Deployment Guide**: Provide instructions for deploying the script to AWS or Google Cloud.

