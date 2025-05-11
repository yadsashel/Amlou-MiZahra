# Amlou MiZahra

**Amlou MiZahra** is an e-commerce platform that specializes in selling Amlou, a Moroccan traditional spread made from roasted almonds, argan oil, and honey. This platform allows users to browse and order Amlou products online, with a smooth, user-friendly interface for both customers and admins. The system includes worker authentication, order management, and professional PDF export for delivery orders.

## Features

- **User Registration & Authentication**: Secure registration and login for workers with access control to admin features.
- **Product Ordering**: Customers can browse and place orders for Amlou products, with clear product descriptions and pricing.
- **Admin Dashboard**: Admins can manage orders, edit details, and export orders as professional PDFs for delivery.
- **PDF Export**: Export order details as a professional PDF, complete with a company logo for branding.
- **Responsive Design**: The site is optimized for both desktop and mobile views.

## Project Structure

```bash
AmlouMiZahra/
├── __pycache__/                 # Compiled Python files
├── static/                      # Static files (CSS, JavaScript, Images)
│   ├── assests/                 # Images and other assets
│   ├── css/                     # CSS styles
│   ├── scripts/                 # JavaScript files
├── templates/                   # HTML templates (Jinja2)
│   ├── admin.html               # Admin dashboard
│   ├── home.html                # Homepage
│   ├── login.html               # Login page
│   ├── order_1.html             # Order page for product 1
│   ├── order_2.html             # Order page for product 2
│   ├── order_3.html             # Order page for product 3
│   ├── order_4.html             # Order page for product 4
│   ├── order_5.html             # Order page for product 5
│   ├── order_6.html             # Order page for product 6
│   ├── product.html             # Product listing page
│   ├── register.html            # Registration page
├── app.py                        # Flask application
├── requirements.txt             # List of required Python packages
├── .gitignore                   # Git ignore file
