# LittleLemonDRF

This is a model backend for a restaurant built with Django Rest Framework.

![Django rest framework](https://github.com/k-cardon/LittleLemonDRF/assets/124483308/4469b797-b5a6-4230-ba1d-c06a1950f6ad)

## How I Made This

Tech used: Django, Django Rest Framework (DRF), Insomnia

This restaurant API allows managers to add and categorize menu items (and add users to "manager" and "delivery" permissions), allows customers to add items to a shopping cart and submit orders, and allows delivery crew to view orders assigned to them by managers. I used DRF generic class-based views as often as possible to simplify permissions and to reduce the amount of code. For the more complicated views, such as the shopping cart, I wrote custom function-based views. I tested the API using Insomnia.

## Lessons Learned

I came to really value DRF for the way it facilitates API construction. For straightforward CRUD functionality and permissions, using DRF's class-based views gave me more time to figure out the complex views and irregular permission patterns.
