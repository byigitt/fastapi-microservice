# FastAPI Microservice Example with Kafka

This project demonstrates a simple microservice architecture using FastAPI and Kafka for inter-service communication. It's designed for educational purposes to understand the basics of microservices, event-driven architecture, and message brokers.

## Architecture Overview

The project consists of three microservices:

1. **Product Service** - Manages product data
2. **Order Service** - Manages order data and listens for product events
3. **Database Service** - An in-memory database that listens for events from other services

Services communicate with each other using Kafka as a message broker. When an action occurs in one service (e.g., creating a product), it publishes an event to Kafka. Other services listen for these events and react accordingly.

## Directory Structure

```
├── docker-compose.yml
├── infrastructure/
│   └── kafka_client.py
├── requirements.txt
└── services/
    ├── product_service/
    ├── order_service/
    └── database_service/
```

## Prerequisites

- Docker and Docker Compose
- Python 3.9+

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/byigitt/fastapi-microservice.git
cd fastapi-microservice
```

2. Build and start the services:

```bash
docker-compose up --build
```

This will start all three services along with Kafka and Zookeeper.

## Service Endpoints

### Product Service (http://localhost:8000)

- `GET /products` - Get all products
- `GET /products/{product_id}` - Get a specific product
- `POST /products` - Create a new product
- `PUT /products/{product_id}` - Update a product
- `DELETE /products/{product_id}` - Delete a product

### Order Service (http://localhost:8001)

- `GET /orders` - Get all orders
- `GET /orders/{order_id}` - Get a specific order
- `GET /customers/{customer_id}/orders` - Get all orders for a customer
- `POST /orders` - Create a new order
- `PUT /orders/{order_id}` - Update an order
- `POST /orders/{order_id}/cancel` - Cancel an order

### Database Service (http://localhost:8002)

- `GET /collections` - Get all collections
- `GET /collections/{collection}` - Get all records in a collection
- `GET /collections/{collection}/{record_id}` - Get a specific record

## Example Usage

1. Create a product:

```bash
curl -X 'POST' \
  'http://localhost:8000/products' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "category": "electronics",
  "stock_quantity": 10
}'
```

2. Create an order:

```bash
curl -X 'POST' \
  'http://localhost:8001/orders' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "items": [
    {
      "product_id": "YOUR_PRODUCT_ID_FROM_STEP_1",
      "quantity": 1,
      "unit_price": 999.99
    }
  ]
}'
```

3. View data in the database service:

```bash
curl -X 'GET' 'http://localhost:8002/collections/products'
curl -X 'GET' 'http://localhost:8002/collections/orders'
```

## Understanding Kafka Communication

1. When a product is created, the Product Service publishes a "product_created" event to Kafka.
2. The Database Service listens for this event and stores the product data.
3. If the Order Service needs to know about product changes (e.g., if a product is deleted), it also listens for product events.

This demonstrates how services can communicate asynchronously without direct dependencies on each other.

## Educational Purpose

This project is designed for learning and doesn't include:

- Authentication and authorization
- Persistence (all data is in-memory)
- Error handling for all edge cases
- Production-ready configurations

For a production environment, you'd want to add these features and use a persistent database.

## License

MIT
