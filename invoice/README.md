# AI Invoice Extraction System for Freelancers

## Table of Contents

1. [Overview](#overview)
2. [High Level Logic](#high-level-logic)
3. [Fine Grained Logic](#fine-grained-logic)
4. [Components](#components)
5. [Assumptions](#assumptions)
6. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
7. [Tools & Technologies](#tools--technologies)
8. [Limitations & Tests](#limitations--tests)
9. [License](#license)

---

## Overview

This project implements an AI-based system that automates the extraction of invoice data for freelancers. Instead of manually typing invoice details, the system processes scanned or photographed invoice images from Google Drive and summarizes them into structured CSV files, greatly simplifying bookkeeping and reporting.
[Image Processing and Metadata Extraction](images/invoice.gif).

---

## High Level Logic

1. **Google Drive Invoice Image Collection:**  
   Downloads invoice images from a configured folder on Google Drive.

2. **Multi-Attempt Data Extraction via LLM:**  
   Each image is processed with up to 5 attempts using different prompts to extract **valid** invoice data in JSON format. Validity is based on strict financial rules.

3. **Structured Output Generation:**  
   Produces:
   - CSV file with extracted **expenses**
   - CSV file with extracted **revenues**
   - CSV file for **failed** extractions
   - A folder with failed images for manual inspection

---

## Fine Grained Logic

### **Invoice Image Collection**
- Authenticates with the user’s Google Drive.
- Retrieves only **unprocessed** invoice images.
- Each image is recorded in a local **SQLite database** to ensure idempotency.

### **LLM-based JSON Extraction with Validation**
- The system attempts up to 5 LLM calls to generate a valid JSON representation of the invoice.
- After each failed attempt, the system refines the prompt and retries using feedback from the previous attempt.
- A JSON is considered **valid** if it passes the following checks:
  1. `"total_price" == "total_price_before_VAT" + "VAT_amount"`
  2. `"VAT_rate" == VAT_amount / total_price_before_VAT"`

- All JSON attempts and results (valid/invalid) are logged and stored.

### **Output Generation**
- If valid JSON is extracted, the invoice is categorized as either:
  - **Revenue** (e.g. client-issued invoice)
  - **Expense** (e.g. supplier invoice)
- Generates:
  - `revenue.csv`
  - `expenses.csv`
  - `failed.csv`
- Stores failed images locally in a dedicated folder for manual review.

---

## Components

- **Google Drive Authentication:**
  Connects to Google Drive folder.

- **SQLite Layer:**  
  Maintains records of all processed and unprocessed images and their metadata.

- **LLM Interaction Layer:**  
  Manages prompt creation, iterative retries and integrity logic.

- **Output Generator:**  
  Output revenues, expenses and failed image CSV files.

---

## Assumptions

- Invoice images are stored in a single Google Drive folder.
- Invoices follow a common structure where totals and VAT are explicitly stated.

---

## Getting Started

### Prerequisites

- Python version 3.12+
- Google Cloud credentials with Drive API access
- OpenAI API Key

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/orlevit/invoice_system
   cd invoice
   ```
2. **Create and Activate Virtual Environment:**
   ```bash
    python -m venv venv
    source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
    pip install -r requirements.txt
   ```
4. **Set up constants:**
    a. Set up .env file with *OPENAI_API_KEY*.
    b. In *invoice_config.py*, change in *FOLDER_ID* for the Google Drive folder ID.

5. **Run the Pipeline:**
   ```bash
   python main.py
   ```

## Tools & Technologies
- OpenAI ChatGPT API
- Google Drive API
- SQLite
- Python

## Limitations & Tests
- Invoices with unusual structures may fail after all 5 attempts.
- Failed invoice processing is manual.
- The OCR is done only through ChatGPT.

## License
This project is licensed under the MIT License.
