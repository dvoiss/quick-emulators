# Quick Emulators

Launch your Android emulators (Genymotion and AVDs) via Spotlight: ⌘ + Space

[![Android Arsenal](https://img.shields.io/badge/Android%20Arsenal-Quick%20Emulators-brightgreen.svg?style=flat)](https://android-arsenal.com/details/1/4620)

![Finding Genymotion Emulator](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/find-genymotion.png)

## Use

```bash
brew tap dvoiss/tap
brew install quick-emulators
brew services start dvoiss/tap/quick-emulators
```

## How does it work?

The process started by `brew services` will create `.app` files under the directory: `~/Applications/Quick Emulators/` (see screenshot below). These empty app files are indexed by Spotlight. They contain a shell script that launches one of these commands:

1. For Android Virtual Devices:

    `PATH_TO_ANDROID_SDK/tools/emulator -avd <name-of-emulator>`

2. For Genymotion Virtual Machines:

    `/Applications/Genymotion.app/Contents/MacOS/player.app/Contents/MacOS/player --vm-name <name-of-emulator>`

For AVDs an `ANDROID_SDK` or `ANDROID_HOME` environment variable must be set. For Genymotion the Genymotion app must be at the default path above.

The background daemon watches for changes in the default locations that AVDs and Genymotion virtual machines are installed to: `~/.android/avd/` and `~/.Genymobile/Genymotion/deployed/`. When you add or remove a new emulator the generated folder containing the .app files gets re-written. For more information see the `plist` method in the [Homebrew formula for Quick Emulators](https://github.com/dvoiss/homebrew-tap/blob/master/quick-emulators.rb).

![Generated App files](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/app-folder.png)

The generated app files are tagged with "Emulator" and either "AVD" or "Genymotion". These tags can be used in Spotlight as well:

![Finding AVD by Tag](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/find-avd.png)

## Caveats:

Genymotion and Android virtual devices cannot run side by side due to the error below. This happens whether you launch them using Quick Emulators or via a different method. The message below occurs while running a Genymotion emulator.

```bash
$ emulator -avd <device-name>
...
emulator: ERROR: Unfortunately, there's an incompatibility between HAXM
hypervisor and VirtualBox 4.3.30+ which doesn't allow multiple hypervisors
to co-exist.  It is being actively worked on; you can find out more about
the issue at http://b.android.com/197915 (Android) and
https://www.virtualbox.org/ticket/14294 (VirtualBox)

Internal error: initial hax sync failed
```