# dcp1610
An experimental implementation of Brother network scanner protocol.

## Quickstart

##### Install
```
git clone https://github.com/Equidamoid/dcp1610.git
pip install --user dcp1610
```
Make sure you have your `<USER_BASE>/bin` in `$PATH`. To get your `USER_BASE` path, run `python3 -m site |grep USER_BASE`

##### Usage
Searching for the device is not implemented yet, so you have to specify the ip address.

```
# Simple scan, full page, grayscale, 100dpi, output file - scan.png
dcp1016-scan $SCANNER_IP

# Scan top half of the page in color and 400dpi, save as mypage.png
dcp1610-scan --color -H 0.5 -d 400 -o mypage.png
```

See `dcp1610-scan -h` for the list of parameters.

## Known bugs/planned features

##### Scanner discovery
Yeah, typing ip address is boring. Scanner discovery is possible via SNMP.

##### Hardcoded model-specific things
The script probably will not work well with non-flatbed scanners (they have extra "next page" message, I don't know how it looks like and how should I handle it).
Also supported scanning modes may differ from model to model

##### It is slow!
The bottleneck for high-res full page scans is network data transfer (you can hear how it stops when some internal buffer is full), need to implement support for compressed images.

##### Scan button
It is possible to make a "daemon mode" listening for device's scan button.

## Q&A

##### Will it work with my scanner?
To be honest, no idea. I only have DCP-1610W and it works pretty good with it.

##### Will it break my scanner?
I can't guarantee that. Use at your own risk.

##### It does not work. What now?
First, try to file a bug. If you have different scanner than I have, you'll have to use Wireshark and the stock "driver" to get an example of how to talk with your scanner.

It may happen that protocol differs a lot and your device is out of scope for this project.

