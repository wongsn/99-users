# Backend Tech Challenge

This repo details the users microservice of the tech challenge.
- **[User service:](https://users99.herokuapp.com)** Stores information about all the users in the system

### 2) User Service

The user service stores information about all the users on the system. Fields available in the user object:

- `id (int)`: User ID _(auto-generated)_
- `name (str)`: Full name of the user _(required)_
- `created_at (int)`: Created at timestamp. In microseconds _(auto-generated)_
- `updated_at (int)`: Updated at timestamp. In microseconds _(auto-generated)_

#### APIs

#### Root URL
[https://users99.herokuapp.com](https://users99.herokuapp.com)

##### Get all users

Returns all the users available in the db (sorted in descending order of creation date).

```
URL: GET /users

Parameters:
page_num = int # Default = 1
page_size = int # Default = 10
```

```json
Response:
{
    "result": true,
    "users": [
        {
            "id": 1,
            "name": "Suresh Subramaniam",
            "created_at": 1475820997000000,
            "updated_at": 1475820997000000,
        }
    ]
}
```

##### Get specific user

Retrieve a user by ID

```
URL: GET /users/{id}
```

```json
Response:
{
    "result": true,
    "user": {
        "id": 1,
        "name": "Suresh Subramaniam",
        "created_at": 1475820997000000,
        "updated_at": 1475820997000000,
    }
}
```

##### Create user

```
URL: POST /users
Content-Type: application/x-www-form-urlencoded

Parameters: (All parameters are required)
name = str
```

```json
Response:
{
    "result": true,
    "user": {
        "id": 1,
        "name": "Suresh Subramaniam",
        "created_at": 1475820997000000,
        "updated_at": 1475820997000000,
    }
}
```
