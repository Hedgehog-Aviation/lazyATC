# LazyATC
Tired of sending messages to people with outdated simbrief? Now you can do it 57% faster!

This tool allows you to quickly message pilots to let them know that they've got an issue somewhere in their flight plan. It contains preset templates, requiring only the departure and arrival airports of the offending pilot. Then simply select the right route, and press `ENTER`, then you have a cheery and polite message ready to go, ready to paste into pilot messages.
Auto routing is available as of V1.1.0 - draws from the wonderful Pilot Assist API to serve correct routes, making usage of the tool far easier (Still watch out for V169s though!)

# Installation Instructions
## We offer three ways to use LazyATC - a VatSys plugin, web application, and standalone executable
### Web application
- Simply visit https://atc.bobtube.org - no install required!
### VatSys plugin

#### Manual Method
- Download the VatSys plugin zip archive from the [latest release](github.com/Hedgehog-Aviation/lazyATC/releases/latest)
- Unblock the zip file by right-clicking on it, selecting Properties, then Unblock
- Extract the zip into `[YOUR CURRENT DRIVE]\Program Files (x86)\vatSys\bin\Plugins`
- Make sure the zip file is unblocked **before** attempting to extract or use the plugin
#### Automatic Method
- Install using the [VatSysManager app](https://github.com/Hedgehog-Aviation/vatManager-fork)
### Standalone executable (Not recommended, currently not high priority)
- Simply install the Standalone exe from the [latest release](github.com/Hedgehog-Aviation/lazyATC/releases/latest) and run.
- You may need to press "keep" or "Download anyway" in some browsers, if they prompt you

# Usage Instructions
### There are two modes, the "Route" and "Altitude" modes.
#### Route mode: 
- Enter the aircraft's planned arrival and departure aerodromes in ICAO format
- Press "Generate"
- Select a valid route and press `ENTER`
- Now you will have the following message copied to your clipboard: `Hi, your planned route seems to be invalid. Can you accept amended routing via {route}?`
#### Altitude mode (Not recommended, easier to simply ask on frequency)
- Enter the aircraft's planned altitude
- Press "Generate"
- Now you will have the following message copied to your clipboard: `Hi, your altitude is non-standard. I can offer you either {fl1} or {fl2}.`


<sub> LazyATC is not an official product of VATSIM, VATPAC, or VatSys. It is a tool designed for personal use. Absolutely no warranty is provided. Use of the tool is at the user's discretion. Not for commercial use. </sub>
