# Invoice and Bill Generator Web Application

## About
This is a web application developed using Python Flask to create invoices, calculate bill totals, store invoice records, search customer invoices, and download invoices as PDF files.

## Features
- Create invoices with multiple products
- Automatically calculate subtotals and grand total
- Download invoices as PDF files
- Store invoice records using SQLite
- View previous invoices
- Search invoices by customer name
- Delete invoice records

## Technologies Used
- Python
- Flask
- HTML and CSS
- SQLite
- ReportLab

## Installation

1. Install Python on your computer.
2. Download or clone this repository.
3. Open the project folder in a terminal.
4. Install the dependencies:

   `pip install -r requirements.txt`

5. Run the application:

   `python app.py`

6. Open `http://127.0.0.1:5000/` in your browser.

## Project Structure

```text
Invoice-Bill-Generator/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
└── templates/
    ├── index.html
    └── history.html
```

## Purpose
This project demonstrates Python web development, database integration, invoice calculations, and PDF generation.
