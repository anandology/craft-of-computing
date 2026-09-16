# craft

Craft is a system for installing required software on students computers and pull updates. 

The interface is a shell script `craft.sh` that installs the required system packages, adds files to be used in the class.

## Intended Audience

The intended audience for this tool are the students of "The Craft of Computing" Course. Many of them are using Linux in WSL amd some are using Linux directly or Mac. This works for all of them.

## Install 

Install it using:

```
curl -fsSL https://craft-of-computing.anandology.com/2026/install.sh | bash
```

## How to add a new version

To create a new version with upgrade.sh

```
versions/v8
└── upgrade.sh
```

And update latest_version.txt to the version number (8, not v8).

The versions directority may have other supporting files and the upgrade.sh will have access to those file.
