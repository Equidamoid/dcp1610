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

```
# Simple scan, full page, grayscale, 100dpi, output file - scan.png, find the scanner automatically
dcp1016-scan

# Scan top half of the page in color and 400dpi, save as mypage.png
dcp1610-scan --color -H 0.5 -d 400 -o mypage.png
```

The script will try to find the scanner in your local network using zeroconf request. In some cases (nasty routers, wicked network configuration, etc) the discovery may fail, like that:
```
% dcp1610-scan
[2017-07-30 22:14:30,130] Querying MDNS for _scanner._tcp.local.
[2017-07-30 22:14:35,347] No scanner found in 5 sec
Traceback (most recent call last):
  File "./dcp1610-scan", line 48, in <module>
    main()
  File "./dcp1610-scan", line 39, in main
    address, name = dcp1610.discovery.find_scanner()
TypeError: 'NoneType' object is not iterable
```

In this case (or if you want to save couple of seconds on discovery) you may specify the scanner ip as a positional argument:
```
dcp1016-scan 192.168.1.5
```

See `dcp1610-scan -h` for the list of parameters.

## Known bugs/planned features

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

