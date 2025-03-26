# Raspberry Pi Code

<details>
  <summary><strong>Table of Contents</strong></summary>

- [Raspberry Pi 5](#raspberry-pi-5)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
- [Raspberry Pi Pico](#raspberry-pi-pico)
  - [Requirements](#requirements-1)
  - [Installation](#installation-1)
  - [Usage](#usage-1)
- [Web App](#web-app)
  - [Requirements](#requirements-2)
  - [Installation](#installation-2)
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

### Requirements

TODO

### Installation

TODO

### Usage

TODO

## Raspberry Pi Pico

### Requirements

TODO

### Installation

TODO

### Usage

TODO

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
