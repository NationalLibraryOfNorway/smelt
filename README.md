# Smelt
Smelt is a GUI application built using PyQt5 for video and audio processing. The application uses FFmpeg to handle various tasks such as combining audio files, converting video formats, and more. This tool is particularly useful for handling multi-channel audio files and different video formats in a streamlined way.

## Features
 - Select and combine multi-channel audio files: Combine separate audio files (e.g., left, right, center, LFE, etc.) into a single audio file.
 - Convert video formats: Convert DPX, MXF, and MOV files to various formats including Prores 422 HQ and H264 MP4.

## Requirements
 - **FFmpeg**

## Smelt Installation Guide

### Windows Installation

1. **Download the Smelt Executable:**
   - Go to the [Releases](https://github.com/NationalLibraryOfNorway/smelt/releases) page of the Smelt GitHub repository.
   - Download the `Smelt.exe` file from the latest release.

2. **Install FFmpeg:**
   - Go to the [FFmpeg Download](https://ffmpeg.org/download.html) page.
   - Download the FFmpeg build for Windows.
   - Extract the contents of the downloaded archive to a folder of your choice (e.g., `C:\ffmpeg`).
   - Add FFmpeg to your system PATH:
     - Open the Start Menu, search for "Environment Variables" and select "Edit the system environment variables."
     - In the System Properties window, click on the "Environment Variables" button.
     - Under "System variables," find the `Path` variable and click "Edit."
     - Click "New" and add the path to the `bin` directory of the FFmpeg folder (e.g., `C:\ffmpeg\bin`).
     - Click "OK" to close all windows.

3. **Run the Smelt Application:**
   - Double-click the downloaded `Smelt.exe` file to run the application.

## Linux Installation

1. **Download the Smelt Executable:**
   - Go to the [Releases](https://github.com/NationalLibraryOfNorway/smelt/releases) page of the Smelt GitHub repository.
   - Download the `smelt-executable-linux.tar.gz` file from the latest release.

2. **Install FFmpeg:**
   - Open a terminal.
   - Install FFmpeg using your package manager. For example, on Ubuntu or Debian-based systems, run:
     ```sh
     sudo apt update
     sudo apt install ffmpeg
     ```
   - On Fedora-based systems, run:
     ```sh
     sudo dnf install ffmpeg
     ```

3. **Unzip the Smelt Executable:**
   - Navigate to the directory where you downloaded the `smelt-executable-linux.tar.gz` file.
   - Extract the contents:
     ```sh
     tar -xvzf smelt-executable-linux.tar.gz
     ```
   - Change permissions to make the extracted file executable:
     ```sh
     chmod +x Smelt
     ```

4. **Run the Smelt Application:**
   - Run the application by executing:
     ```sh
     ./Smelt
     ```

---

For any additional questions or issues, please refer to the [issues](https://github.com/NationalLibraryOfNorway/smelt/issues) section on GitHub.
