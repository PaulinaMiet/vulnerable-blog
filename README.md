# Vulnerable Blog Application – OWASP Top 10 Educational Project

This project presents a deliberately vulnerable web application created for educational purposes. It allows testing and understanding selected web application vulnerabilities based on the [OWASP Top 10](https://owasp.org/www-project-top-ten/) list (2021 edition).

The app is a simple blog created using Flask (Python), with basic features like login, post creation and display, as well as a built-in search. It includes five example vulnerabilities that can be tested and optionally mitigated.

## Project Goal

The aim was to implement a web service containing selected OWASP Top 10 vulnerabilities in a controlled environment, and test its behavior using security scanners. For each vulnerability, the project includes:

- a working insecure version,
- a brief explanation,
- and an example fix or countermeasure.

## Included Vulnerabilities

The following OWASP Top 10 vulnerabilities are demonstrated in the project:

- **A01: Broken Access Control**  
  Example: bypassing access restrictions by modifying the URL manually

- **A02: Cryptographic Failures**  
  Example: storing plaintext passwords; optional fix using Argon2id hashing

- **A03: Injection**
  
  Examples:
  - SQL Injection (basic example in search function)
  - Cross-Site Scripting (XSS) via stored post content

- **A05: Security Misconfiguration**  
  Example: exposing debug stack trace and internal app details

- **A08: Software and Data Integrity Failures**  
  Example: unsigned cookies that can be modified manually to impersonate users

## Stack

- Python 3.x
- Flask
- SQLite3
- HTML + basic Jinja templates

## Vulnerability Scanners Used

The project was tested using several open-source tools:

- **Nikto**
- **Wapiti**
- **ZAP (Zed Attack Proxy)**
