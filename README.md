# Raspberry Pi Code

<details>
  <summary><strong>Table of Contents</strong></summary>

- [Raspberry Pi 5](#raspberry-pi-5)
  - [Method 1 - PyInstaller](#method-1---pyinstaller)
    - [Requirements](#requirements)
    - [Building](#building)
    - [Usage](#usage)
  - [Method 2](#method-2)
    - [Requirements](#requirements-1)
    - [Installation](#installation)
    - [Usage](#usage-1)
- [Raspberry Pi Pico](#raspberry-pi-pico)
  - [Requirements](#requirements-2)
  - [Setup](#setup)
- [Web App](#web-app)
  - [Requirements](#requirements-3)
  - [Installation](#installation-1)
  - [Usage](#usage-2)
- [Troubleshooting](#troubleshooting)
  - [Liboqs](#liboqs)
- [Misc.](#misc)
- [License](#license)

</details>

This code is already setup on the Raspberry Pi 5s and Raspberry Pi Picos, so only the [Usage](#usage) section needs to be looked at. However, we have also included additional instructions below just in case you want to change the code yourself and test things out.

The code is split into 3 main parts:

1) `main/` - this includes all the code used on the Raspberry Pi 5s.

2) `pico/` - this includes all the code used on the Raspberry Pi Picos.

3) `web-app/` - this includes the code for the simple web application which displays the current active users (ESP32s) the Raspberry Pi 5 is searching for, and their distance to the Raspberry Pi 5.

## Raspberry Pi 5

There are 2 methods to setup and run this code. The first is much easier to setup and is therefore recommended.

### Method 1 - PyInstaller

#### Requirements

- Pyinstaller (Python)

#### Building

To build the application, run the following command after navigating to `main/`:

```bash
pyinstaller pyinstaller.spec
```

#### Usage

From the same directory, run the following command to run the script:

```bash
./dist/proximity_gateway/proximity_gateway
```

### Method 2

#### Requirements

- Pip (Python)

#### Installation

To install all the dependencies, run the following command from the `main/` directory:

```bash
pip install -r requirements.txt
```

#### Usage

To run the script from the same directory, run the following command:

```bash
python main.py
```

## Raspberry Pi Pico

### Requirements

- CircuitPython

- Thonny

### Setup

Open `pico-hid.py` with Thonny and save the file to the Pico with the filename `code.py`. This is enough to get it so that whenever the Pico gets power, it will automatically run the contents of the file.

## Web App

### Requirements

- NodeJS

### Installation

First, navigate to the `web-app/` directory. Then, run the following command to install the necessary packages:

```bash
npm install
```

### Usage

From the same directory as [Installation](#installation-2), run the following command to run the website:

```bash
npm run dev
```

## Troubleshooting

### Liboqs

Refer to the [open quantum safe liboqs get started page](https://openquantumsafe.org/liboqs/getting-started.html).

## Misc.

TODO

## License

This project is licensed under the terms of the MIT license. Refer to [LICENSE](LICENSE) for more information.
