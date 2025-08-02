

# 🧠 AI-Powered Business Chatbot for E-Commerce & Ayurveda Intelligence

An intelligent, end-to-end business chatbot integrating **Meta WhatsApp Business API**, **Shopify Admin API**, and **Google Gemini LLM** to automate customer interactions, resolve order queries, and provide personalized **Ayurveda-based product recommendations** — all through WhatsApp.


## 🚀 Features

- 💬 **Conversational AI** via WhatsApp (Meta Business API)
- 🛒 **Shopify Integration** for real-time order queries & product details
- 🌿 **Ayurveda Intelligence** using Gemini Pro LLM for restricted items, combos & coupon logic
- 🔁 **Automation of e-commerce workflows** — order tracking, reordering, coupon application
- 📈 **Performance optimization** through prompt engineering and latency tuning

---

## 🧩 Tech Stack

| Layer              | Tools / Frameworks |
|--------------------|--------------------|
| **Frontend**       | WhatsApp (Chat UI) |
| **Backend**        | Python, Flask      |
| **AI & LLMs**      | Google Gemini Pro, LangChain |
| **APIs Integrated**| Meta WhatsApp Cloud API, Shopify Admin API |
| **Testing**        | Postman, NGROK, Firebase (Webhooks) |
| **DevOps**         | Git, GitHub        |

---

## 📌 Use Cases

- ✅ Real-time order tracking & customer support
- ✅ Personalized Ayurveda-based product suggestions
- ✅ Combo deals and coupon logic via AI
- ✅ Business process automation (customer queries to checkout)

---

## 🧠 Architecture Overview

```mermaid
graph TD
A[User on WhatsApp] --> B[Meta WhatsApp Cloud API]
B --> C[Flask Backend Server]
C --> D[Shopify Admin API]
C --> E[Gemini Pro LLM]
E --> F[Ayurveda Knowledge Prompting]
D --> G[Order Status, Products]
C --> H[Response back to WhatsApp]
