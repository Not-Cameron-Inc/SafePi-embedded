```mermaid
sequenceDiagram
    autonumber
    AndroidApp->>Webserver: I need a token.
    Webserver->>AndroidApp: Token:lkjsbdcoiyu3927ghibjkabsd
    create participant RPi
    AndroidApp->>RPi: Token:lkjsbdcoiyu3927ghibjkabsd
    RPi->>Webserver: Token:lkjsbdcoiyu3927ghibjkabsd
    Webserver->>RPi: Connection Confirmed
```