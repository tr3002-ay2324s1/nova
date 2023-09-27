# Brio

The Smart Habit Tracker.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)

## Getting Started

These instructions will help you get the project up and running on your local machine.

### Prerequisites

- Python (version specified in `requirements.txt`)
- Virtual environment tool (e.g., `venv` or `virtualenv`)
- Git (for cloning the repository)

### Setup

- Create and activate a virtual environment:

  - Using venv (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```

  - Using virtualenv:

    ```bash
    virtualenv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```

- Install the project dependencies:

  ```bash
  pip install -r requirements.txt
  ```

- Install project secrets:

  Install Doppler CLI for secret management:

  - **Mac OS / Linux**

    ```bash
    # Prerequisite. gnupg is required for binary signature verification
    brew install gnupg

    # Next, install using brew (use `doppler update` for subsequent updates)
    brew install dopplerhq/cli/doppler
    ```

  - **Windows**

    ```powershell
    # winget is the recommended installation method
    winget install doppler

    # Scoop is also supported
    scoop bucket add doppler https://github.com/DopplerHQ/scoop-doppler.git
    scoop install doppler

    # WSL is supported. Just follow the Shell Script process or the process
    # for the OS you're using inside WSL (it defaults to Ubuntu).

    # Git Bash is also supported
    mkdir -p $HOME/bin
    curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh -s -- --install-path $HOME/bin

    # When using Git Bash, your initial login and other operations requiring
    # interactive input will need to use `winpty` due to this bug:
    # https://github.com/skratchdot/open-golang/issues/34
    #
    # winpty doppler login
    ```

  - Verify CLI & Login to Doppler

  ```bash
  doppler --version # Verify CLI is installed

  doppler login # Login to Doppler
  ```

  - Setup Project

  ```bash
  doppler setup # Setup project using doppler.yaml
  ```

  You can now run projects without an env! 🎉

## Usage

Explain how to run or use your project here.

To start the bot, run this command and then head to [t.me/brio_tracker_bot](https://t.me/brio_tracker_bot)

```bash
doppler run --command "python3 bot.py"
```
