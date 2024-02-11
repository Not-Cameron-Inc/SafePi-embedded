```mermaid
---
title: Encryption Scheme
---
flowchart
    AndroidApp -->|TLS| Webserver
    Webserver --> |something| AndroidApp
    Webserver -->|AES| RPi
    RPi -->|RSA| AndroidApp

```