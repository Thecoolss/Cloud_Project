# FoodExpress - Serverless Multi-Restaurant Food Ordering Platform

A cloud-based food ordering platform built with Microsoft Azure services, enabling restaurants to register meals and customers to browse and order food in their delivery area.

## 🚀 Project Overview

FoodExpress is a simplified Uber Eats-like platform that demonstrates serverless architecture using Azure Functions and Azure Storage services. The platform supports two-sided interaction between restaurants (who register meals) and customers (who browse and order meals).

## 📋 Features

### For Restaurants
- Register new meals with details (name, description, price, preparation time)
- Set delivery areas for each meal
- Categorize meals and mark dietary preferences

### For Customers
- Select delivery area from dropdown
- Browse available meals in their area
- Add multiple meals to cart with quantity controls
- **Real-time estimated delivery time calculation**
- View order confirmation with delivery estimates
- Responsive design for mobile and desktop

### Key Functionality: Estimated Delivery Time ⏰

The platform calculates estimated delivery time using the rubric formula:

```
Estimated Time = sum(preparation times) + fixed pickup time (10 min) + fixed delivery time (20 min)
```

**Where it's displayed:**
1. **Cart Sidebar** - Shows estimated time as items are added
2. **Checkout Modal** - Displays estimate before order submission
3. **Order Confirmation** - Final delivery estimate after order placement

The calculation accounts for:
- Individual meal preparation times (multiplied by quantity)
- Fixed pickup time at restaurant (10 minutes)
- Fixed delivery travel time (20 minutes)

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Deployment** | GitHub Pages |
| **Backend** | Azure Functions (Python) |
| **Storage** | Azure Table Storage |
| **Advanced** | Azure Queue Storage (for invalid orders) |

## 📁 Project Structure

```
Cloud_Project/
├── frontend/
│   ├── index.html              # Customer page
│   ├── restaurant.html         # Restaurant page
│   ├── css/
│   │   └── style.css          # All styling
│   └── js/
│       ├── api.js             # API communication layer
│       ├── customer.js        # Customer functionality
│       └── restaurant.js      # Restaurant functionality
├── backend/
│   ├── getmeal/
│   │   ├── function.json
│   │   └── getmeals.py        # Get meals by area
│   ├── registermeal/
│   │   ├── function.json
│   │   └── registermeal.py    # Register new meals
│   ├── submitorder/
│   │   ├── function.json
│   │   └── submitorder.py     # Submit customer orders (with time calc)
│   ├── databases/
│   │   └── dgenerate.py       # Data generation script
│   ├── host.json
│   └── requirements.txt
└── README.md
```

## 🔧 Setup & Deployment

### Prerequisites
- Azure subscription
- Azure Functions Core Tools
- Python 3.9+
- GitHub account

### Backend Setup
1. Create Azure Storage Account
2. Create Azure Functions App
3. Configure connection strings in Azure
4. Deploy functions using Azure CLI or VS Code

### Frontend Setup
1. Update `frontend/js/api.js` with your Azure Functions URL
2. Deploy to GitHub Pages
3. Enable CORS in Azure Functions

### Environment Variables
Required in Azure Functions:
- `AzureStorageConnectionString` or `AzureWebJobsStorage`

## 📊 Data Requirements

The platform supports:
- **Minimum 3 delivery areas**: Central, North, South, East, West
- **10+ restaurants per area** (30+ total)
- Meal data includes: name, description, price, preparation time, category

## 🌐 Live Deployment

**GitHub Pages URL**: [Add your GitHub Pages URL here]

## 👥 Team Information

[Add team member names and responsibilities here]

## 📝 API Endpoints

### Get Meals
```
GET /api/meals?area={area}
Returns: List of available meals in specified area
```

### Register Meal
```
POST /api/registerMeal
Body: { name, description, price, preparationTime, deliveryAreas, ... }
Returns: Created meal with ID
```

### Submit Order
```
POST /api/submitOrder
Body: { customerName, deliveryAddress, area, meals, ... }
Returns: Order confirmation with estimated delivery time
```

## 🎨 Design Features

- Modern gradient UI with purple theme
- Responsive design for all screen sizes
- Real-time cart updates
- Smooth animations and transitions
- Toast notifications for user feedback
- Modal-based checkout flow

## 📈 Future Enhancements

- Variable delivery times based on restaurant distance
- Order tracking and status updates
- Restaurant dashboard for managing meals
- Customer order history
- Payment integration
- Real-time notifications

## 📄 License

This project is created for educational purposes as part of Fall 2025 Cloud Computing course.

---

**Powered by Azure Functions & Azure Storage** ☁️