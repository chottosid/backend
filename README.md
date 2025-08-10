# Shohochori Backend

Shohochori is a comprehensive social media platform designed specifically for elderly users, providing social connectivity, health management, community support, and healthcare services. This repository contains the backend API built with Java Spring Boot and Hibernate ORM.

## 🌟 Features

### 1. Social Media Platform
- User registration and authentication for elderly users
- Social media interface with posts, comments, likes, and reactions
- Direct messaging (DM) system
- User profiles and social connections
- News feed with personalized content

### 2. Physical Wellness Management
- Personalized physical activity suggestions
- Medicine reminder system with scheduling
- Wellness routine tracking and reminders
- Health metrics monitoring
- Progress tracking and analytics

### 3. Bondhu (Community Help) System
- Help request creation and management
- Location-based volunteer matching
- Service categories (medical assistance, grocery shopping, transportation, etc.)
- Real-time notification system for nearby volunteers
- Request status tracking and completion

### 4. Doctor Appointments & Telemedicine
- Doctor profile management and discovery
- Appointment scheduling system
- Video conferencing integration for virtual consultations
- Physical appointment booking
- Medical history and prescription management
- Doctor-patient communication portal

## 🛠 Technology Stack

- **Framework**: Django
- **Database**: MySQL
- **Authentication**:  JWT
- **API Documentation**: Swagger/OpenAPI 3.0

## 📋 Prerequisites

- Python 3.11
- Django
- MySQL 8.0+


## 🔧 Key Components

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Elder, Volunteer, Doctor, Admin)
- Password encryption with BCrypt
- Session management


### Services
- **UserService**: User management and authentication, Posts, comments, likes, DM functionality
- **WellnessService**: Health activities, medicine reminders
- **BondhuService**: Help requests and volunteer matching
- **DoctorService**: Appointment management and telemedicine



## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

**Made with ❤️ for the elderly community**
