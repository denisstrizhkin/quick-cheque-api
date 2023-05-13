# Quick Cheque Entities

## User

- ID (PK, int)
- Name (varchar(50))
- Email (UNIQUE, varchar(50))
- Password (varchar(16), min 8, eng letters + numbers)
- Photo Url (varchar(100))

## Room

- ID (PK, int)
- Name (varchar(30))
- OwnerID (FK -> User, int)

## Room <-> User

- RoomID (FK -> Room, int)
- UserID (FK -> User, int)

## Cheque

- ID (PK, int)
- RoomID (FK -> Room, int)
- OwnerID (FK -> User, int)
- Name (varchar(30))

## ProductItem

- ID (PK, int)
- Name (varchar(30))
- Price (int)
- Count (int)
- RoomId (FK -> Room)

## ProductItem <-> User

- ProductID (FK -> ProductItem, int)
- UserID (FK -> User, int)
