```mermaid
---
title: Encryption Scheme
---
flowchart
    AndroidApp -->|TLS/HTTPS| Webserver
    Webserver --> |TLS/HTTPS| AndroidApp
    AndroidApp -->|AES Stored Key| RPi
    RPi -->|AES Stored Key| AndroidApp
    RPi -->|TLS/HTTPS| Webserver
    Webserver -->|TLS/HTTPS| RPi

```