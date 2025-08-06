# Contract Signing Microservice

This project is a backend microservice to manage the workflow of signing contracts or designs.

## Getting Started

### Prerequisites

- Python 3.12
- Poetry

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Mandy-cyber/firma_contratos.git
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a user
    ```bash
    python create_user.py --username <your_username> --password <your_password>
    ```
4.  Run the application:
    ```bash
    uvicorn main:app --reload
    ```

## API Endpoints

The service exposes the following endpoints:

### Authentication

-   **POST /token**

    Authenticates a user and returns a JWT token.

    **Request Body:**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

    **Response:**
    ```json
    {
        "access_token": "your_access_token",
        "token_type": "bearer"
    }
    ```

### Contracts

-   **POST /contracts/**

    Creates a new contract. Requires authentication.

    **Request Body (multipart/form-data):**

    -   `client_data`: A JSON string with the client's name and email.
        ```json
        {
            "name": "Mandy Vega",
            "email": "mandy@ejemplo.com"
        }
        ```
    -   `design_image`: The design image file.
    -   `photo_reference` (optional): A photo reference file.

-   **GET /contracts/{contract_id}/preview**

    Returns a preview of the unsigned contract PDF.

-   **POST /contracts/{contract_id}/sign**

    Signs a contract.

    **Request Body (multipart/form-data):**

    -   `signature_image`: The signature image file.
    -   `signed_by`: The name of the person signing the contract.

-   **GET /contracts/{contract_id}/signed**

    Returns the signed contract PDF.

## Schemas

### ClientData

```json
{
    "name": "string",
    "email": "user@example.com"
}
```

### Contract

```json
{
    "id": "integer",
    "client_name": "string",
    "client_email": "user@example.com",
    "design_image_path": "string",
    "photo_reference_path": "string (optional)",
    "unsigned_pdf_path": "string (optional)",
    "signed_pdf_path": "string (optional)",
    "signer_ip": "string (optional)",
    "signer_user_agent": "string (optional)"
}
```
